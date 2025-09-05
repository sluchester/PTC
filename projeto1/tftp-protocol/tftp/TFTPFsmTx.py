from enum import Enum, auto
from tftp.TFTPPacket import WRQPacket, DataPacket, AckPacket, ErrorPacket, TFTPPacket
from pypoller import poller
import os

# Define os estados da máquina de estados finita (FSM) para a transmissão de arquivos TFTP.
# Os estados são: INIT (inicialização), TX (transmissão de dados),
# ULTIMA (último bloco de dados), FIM (finalização) e ERRO (erro de transmissão).
class EstadoTx(Enum):
    INIT = auto()
    TX = auto()
    ULTIMA = auto()
    FIM = auto()
    ERRO = auto()

# Classe FEMTransmissao implementa a máquina de estados para
# a transmissão de arquivos TFTP. Ela herda de poller.Callback
# para lidar com eventos de transmissão e timeouts.
# Ela gerencia o envio de pacotes WRQ, DATA e ACK, controla o estado da transmissão
# e lida com erros.
class FEMTransmissao(poller.Callback):
    def __init__(self, client, filename=None, timeout=5):
        if not filename:
            raise ValueError("O nome do arquivo deve ser fornecido.")

        # Verifica se o cliente é uma instância de TFTPClient e seta as demais variáveis
        # para a máquina de estados trabalhar corretamente ao ser construída.
        super().__init__(client.sock, timeout)
        self.client = client
        self.filename = filename
        self.state = EstadoTx.INIT
        self.block_number = 0
        self.terminado = False
        self.last_packet_sent = None
        self.ultima_msg = False

        self._enviar_wrq()

    # Método para enviar o pacote WRQ (Write Request)
    # para o servidor TFTP. Ele cria um pacote WRQ com o nome do arquivo
    # e o envia para o endereço do servidor TFTP.
    # O pacote WRQ é usado para solicitar a escrita de um arquivo no servidor.
    # O pacote contém o nome do arquivo e o modo de transferência ("octet").
    # O opcode para WRQ é 2.
    # O pacote é enviado via socket UDP para o servidor TFTP.
    # Após o envio, uma mensagem é impressa no console indicando que o WRQ foi enviado.
    def _enviar_wrq(self):
        pkt = WRQPacket(self.filename)
        self.client.sock.sendto(pkt.to_bytes(), (self.client.server_ip, self.client.server_port))
        print(f"FEM: WRQ enviado para {self.client.server_ip}:{self.client.server_port}")

    # Método chamado quando a máquina de estados é ativada.
    # Ele registra o callback para receber dados do socket e inicia o processo de transmissão.
    # Se a transmissão já estiver terminada, desativa a máquina de estados e o timeout.
    # Se o socket não estiver definido, não faz nada.
    # Se o socket estiver definido, aguarda a recepção de pacotes do servidor.
    # Se ocorrer um erro durante a recepção, imprime uma mensagem de erro e entra no estado de erro.
    # Se a transmissão for concluída, desativa a máquina de estados e o timeout.
    # Se a transmissão for abortada por erro, imprime uma mensagem de erro.
    # Se a transmissão for abortada por timeout, imprime uma mensagem de timeout.
    def handle(self):
        if self.fd is None:
            return

        try:
            data, addr = self.fd.recvfrom(516)
            # print(f"FEM: Pacote bruto recebido de {addr}: {data[:10]}... len={len(data)}")
            try:
                packet = TFTPPacket.from_bytes(data)
                # print(f"FEM: Pacote interpretado: {type(packet).__name__}")

            except ValueError as e:
                print(f"FEM: Erro de parsing: {e}")
                self.state = EstadoTx.ERRO
                self.terminado = True
                return

            self.recebido = (packet, addr)
            self.mef()

        except Exception as e:
            print(f"FEM: Erro no handle(): {e}")
            self.state = EstadoTx.ERRO
            self.terminado = True

        if self.terminado:
            print("FEM: Transmissão encerrada.")
            self.disable()
            self.disable_timeout()

    # Método que processa o estado atual da FSM.
    # Dependendo do estado atual, chama o método apropriado para lidar com a lógica de
    # transmissão de arquivos TFTP.
    def mef(self):
        if self.state == EstadoTx.INIT:
            self.handle_init()
        elif self.state == EstadoTx.TX:
            self.handle_tx()
        elif self.state == EstadoTx.ULTIMA:
            self.handle_ultima()
        elif self.state == EstadoTx.FIM:
            self.handle_fim()
        elif self.state == EstadoTx.ERRO:
            self.handle_erro()

    # O método handle_init() lida com o estado de inicialização, esperando receber o
    # primeiro ACK do servidor após enviar o WRQ. Se receber um ACK com o número de bloco 0,
    # inicia a transmissão do primeiro bloco de dados. Se receber um pacote de erro, entra no estado de erro.
    def handle_init(self):
        packet, addr = self.recebido
        if isinstance(packet, AckPacket) and packet.block_number == 0:
            self.remote_tid = addr
            self.block_number = 1
            self._enviar_data()
        elif isinstance(packet, ErrorPacket):
            print(f"FEM[INIT]: Erro recebido: {packet.error_msg}")
            self.state = EstadoTx.ERRO
            self.terminado = True
        else:
            print("FEM[INIT]: Pacote inesperado.")

    # O método handle_tx() lida com o estado de transmissão, esperando receber ACKs 
    # dos blocos de dados enviados.
    # Se receber um ACK com o número de bloco correto, envia o próximo bloco de dados.
    # Se receber um ACK para o último bloco, muda o estado para ULTIMA e chama o método mef() 
    # para processar o estado final.
    # Se receber um pacote de erro, entra no estado de erro e seta a transmissão como terminada.
    def handle_tx(self):
        packet, _ = self.recebido
        if isinstance(packet, AckPacket) and packet.block_number == self.block_number:
            if self.ultima_msg:
                self.state = EstadoTx.ULTIMA
                self.mef()
            else:
                self.block_number += 1
                self._enviar_data()
        elif isinstance(packet, ErrorPacket):
            print(f"FEM[TX]: Erro recebido: {packet.error_msg}")
            self.state = EstadoTx.ERRO
            self.terminado = True

    # O método handle_ultima() lida com o estado final da transmissão,
    # onde espera receber o ACK do último bloco de dados enviado.
    # Se receber um ACK com o número de bloco correto, muda o estado para FIM
    # e seta a transmissão como terminada.
    def handle_ultima(self):
        packet, _ = self.recebido
        if isinstance(packet, AckPacket) and packet.block_number == self.block_number:
            self.state = EstadoTx.FIM
            self.terminado = True
            print(f"FEM[ULTIMA]: Recebido {type(packet).__name__} bloco {packet.block_number}")

    # Se a transferência for concluída, imprime uma mensagem de sucesso.
    def handle_fim(self):
        print("FEM[FIM]: Transmissão finalizada com sucesso.")

    # Se ocorrer qualquer anormalidade, o estado de erro imprime uma mensagem de erro.
    def handle_erro(self):
        print("FEM[ERRO]: Transmissão abortada.")

    # Método para enviar um ACK (Acknowledgment) para o servidor TFTP.
    # O ACK confirma o recebimento de um bloco de dados.
    # Ele cria um pacote ACK com o número do bloco recebido e o envia para o endereço remoto.
    def _enviar_data(self):
        try:
            with open(self.filename, 'rb') as f:
                f.seek((self.block_number - 1) * 512)
                data = f.read(512)
                pkt = DataPacket(self.block_number, data)
                self.last_packet_sent = pkt
                self.client.sock.sendto(pkt.to_bytes(), self.remote_tid)
                print(f"FEM: Enviado DATA {self.block_number} ({len(data)} bytes)")
                self.ultima_msg = len(data) < 512
                self.state = EstadoTx.TX
        except Exception as e:
            print(f"FEM: Erro ao ler arquivo: {e}")
            self.state = EstadoTx.ERRO
            self.terminado = True

    # Método para lidar com timeouts.
    # Ele imprime uma mensagem de timeout detectado e reenviará o último pacote enviado.
    def handle_timeout(self):
        print("FEM: Timeout detectado. Reenviando último pacote.")
        if self.last_packet_sent:
            self.client.sock.sendto(self.last_packet_sent.to_bytes(), self.remote_tid)