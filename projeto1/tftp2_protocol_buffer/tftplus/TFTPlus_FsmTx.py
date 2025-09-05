# Realiza a importação de módulos necessários para construir os pacotes TFTP2 
    # e gerenciar a máquina de estados.
# Importa a classe TFTP2_ProtoPacket para manipulação de pacotes TFTP2,
    # e a classe poller.Callback para gerenciar eventos de transmissão de dados.
from enum import Enum, auto
from tftplus.TFTPlus_ProtoPacket import TFTP2_ProtoPacket
from pypoller import poller

# Enum que define os estados possíveis da FSM de transmissão
class EstadoTx(Enum):
    INIT = auto()
    TX = auto()
    ULTIMA = auto()
    FIM = auto()
    ERRO = auto()

# Classe principal da máquina de estados de transmissão (FSM TX)
# Herda de poller.Callback para poder ser usada no poller (event loop)
class TFTPlus_FsmTx(poller.Callback):
    def __init__(self, client, filename=None, timeout=5):
        if not filename:
            raise ValueError("O nome do arquivo deve ser fornecido.")

        super().__init__(client.sock, timeout)  # Inicializa a classe base do poller com socket e timeout
        self.client = client    # Referência ao cliente (usa IP, porta e socket)
        self.filename = filename    # Nome do arquivo a ser transmitido
        self.state = EstadoTx.INIT  # Estado inicial da FSM
        self.block_number = 0   # Número do bloco atual (começa em 0)
        self.terminado = False  # Flag para indicar se a transmissão foi concluída
        self.last_packet_sent = None    # Último pacote enviado (para reenvio em caso de timeout)
        self.ultima_msg = False # Flag para indicar se é a última mensagem
        self.remote_tid = (self.client.server_ip, self.client.server_port)  # TID remoto (IP e porta do servidor)

    # Monta e seriliza o pacote WRQ a partir da classe TFTP2_ProtoPacket
    # Inicia a transmissão enviando WRQ (Write Request) para o servidor
    # Habilita o timeout para retransmissão em caso de falha
    def start(self):
        msg = TFTP2_ProtoPacket.criar_wrq(self.filename)
        self.last_packet_sent = msg
        data = TFTP2_ProtoPacket.to_bytes(msg)
        self.client.sock.sendto(data, self.remote_tid)
        self.enable_timeout()
        print(f"FEM: WRQ enviado para {self.remote_tid}")

    # Método chamado pelo poller quando há dados disponíveis no socket
    # Recebe os dados, converte para mensagem protobuf e chama a máquina de estados (mef)
    # Trata exceções e erros de recepção
    def handle(self):
        if self.terminado:
            self.disable()
            self.disable_timeout()
            print("FEM: Transmissão concluída.")
            return
        try:
            data, addr = self.fd.recvfrom(1024) # type: ignore
            msg = TFTP2_ProtoPacket.from_bytes(data)
            self.recebido = (msg, addr)
            self.mef()
        except Exception as e:
            print(f"FEM: Erro no handle(): {e}")
            self._erro()

    # Método que processa o estado atual da FSM.
    # Dependendo do estado atual, chama o método apropriado para lidar com a lógica de
        # transmissão de arquivos TFTP2.
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

    # Método que lida com o estado INIT da FSM.
    # Envia o primeiro pacote DATA com o conteúdo do arquivo.
    # Se o pacote ACK for recebido, transita para o estado TX.
    # Se um erro for recebido, transita para o estado ERRO.
    def handle_init(self):
        msg, addr = self.recebido
        if TFTP2_ProtoPacket.tipo(msg) == "ACK" and msg.ack.block_n == 0:
            print(f"[FEM INIT] Recebido primeiro ACK de {addr}, atualizando remote_tid.")
            self.remote_tid = addr
            self.block_number = 1
            self._enviar_data()
        elif TFTP2_ProtoPacket.tipo(msg) == "ERROR":
            print(f"FEM[INIT]: Erro recebido: {msg.error.errormsg}")
            self._erro()
        else:
            print("FEM[INIT]: Pacote inesperado.")

    # Método que lida com o estado TX da FSM.
    # Recebe pacotes ACK do servidor, verifica se o bloco recebido é o esperado.
    # Se for, envia o próximo bloco de dados.
    # Se o ACK for para o último bloco, transita para o estado FIM.
    # Se um erro for recebido, transita para o estado ERRO.
    def handle_tx(self):
        msg, addr = self.recebido
        print(f"FEM[TX]: Recebido tipo={TFTP2_ProtoPacket.tipo(msg)} block_n={msg.ack.block_n} de {addr}")
        # print(f"FEM[TX]: remote_tid esperado={self.remote_tid}, ultima_msg={self.ultima_msg}, block_number esperado={self.block_number}")

        if addr != self.remote_tid:
            print(f"FEM[TX]: TID inválido: esperado {self.remote_tid}, recebido {addr}")
            self._erro()
            return

        if TFTP2_ProtoPacket.tipo(msg) == "ACK" and msg.ack.block_n == self.block_number:
            print("FEM[TX]: ACK correto recebido")
            if self.ultima_msg:
                print("FEM[TX]: Última mensagem detectada, indo direto para FIM.")
                self.state = EstadoTx.FIM
                self.terminado = True
            else:
                self.block_number += 1
                self._enviar_data()
        elif TFTP2_ProtoPacket.tipo(msg) == "ERROR":
            print(f"FEM[TX]: Erro recebido: {msg.error.errormsg}")
            self._erro()
        else:
            print("FEM[TX]: Pacote inesperado recebido. Ignorando.")

    # Método que lida com o estado ULTIMA da FSM.
    # Recebe o ACK final do servidor, verifica se é o esperado.
    # Se for, transita para o estado FIM.
    # Se não for, ignora o pacote.
    # Se o pacote recebido não for ACK, ignora.
    # Esse método era para fazer isso, mas não está sendo usado atualmente.
    # Mesmo assim, fiquei com medo de apagar e, devido ao tempo, deixei ele assim.
    def handle_ultima(self):
        msg, addr = self.recebido
        print(f"FEM[ULTIMA]: Recebido do addr={addr}, remote_tid={self.remote_tid}")
        # print(f"FEM[ULTIMA]: Tipo={TFTP2_ProtoPacket.tipo(msg)} block_n={msg.ack.block_n} esperado={self.block_number}")

        if addr != self.remote_tid:
            print("FEM[ULTIMA]: TID inválido. Ignorando pacote.")
            return

        elif TFTP2_ProtoPacket.tipo(msg) != "ACK":
            print("FEM[ULTIMA]: Pacote recebido não é ACK. Ignorando.")
            return

        elif msg.ack.block_n != self.block_number:
            print(f"FEM[ULTIMA]: Block number inesperado. Esperava {self.block_number}, recebeu {msg.ack.block_n}. Ignorando.")
            return

        else:
            print("FEM[ULTIMA]: ACK final correto recebido. Indo para FIM.")
            self.state = EstadoTx.FIM
            self.terminado = True

    # Método que lida com o estado FIM da FSM.
    # Desabilita a FSM e o timeout, indicando que a transmissão foi concluída.
    # Imprime mensagem de conclusão.
    def handle_fim(self):
        self.disable()
        self.disable_timeout()
        print("FEM[FIM]: Transmissão finalizada.")

    # Método que lida com o estado ERRO da FSM.
    # Imprime mensagem de erro, desabilita a FSM e o timeout.
    # Define a flag de término como True.
    def handle_erro(self):
        print("FEM[ERRO]: Transmissão abortada por erro.")
        self.terminado = True
        self.disable()
        self.disable_timeout()

    # Método que envia o pacote DATA com o conteúdo do arquivo.
    # Lê o arquivo, monta o pacote DATA, envia para o servidor e
        # atualiza o estado para TX e incrementa o número do bloco.
    # Se o tamanho do bloco for menor que 512 bytes, define a flag ultima_msg
        # para True, indicando que é o último bloco a ser enviado.
    # Se ocorrer algum erro ao ler o arquivo, transita para o estado ERRO.
    def _enviar_data(self):
        try:
            with open(self.filename, 'rb') as f:
                f.seek((self.block_number - 1) * 512)
                data_bytes = f.read(512)
                msg = TFTP2_ProtoPacket.criar_data(self.block_number, data_bytes)
                self.last_packet_sent = msg
                data = TFTP2_ProtoPacket.to_bytes(msg)
                self.client.sock.sendto(data, self.remote_tid)
                print(f"FEM: Enviado DATA {self.block_number} ({len(data_bytes)} bytes)")
                self.ultima_msg = len(data_bytes) < 512
                self.state = EstadoTx.TX
        except Exception as e:
            print(f"FEM: Erro ao ler arquivo: {e}")
            self._erro()

    # Método que trata erros de recepção.
    # Define o estado como ERRO, desabilita a FSM e o timeout,
        # e define a flag de término como True.
    def _erro(self):
        print("FEM: Entrando no estado de erro.")
        self.state = EstadoTx.ERRO
        self.terminado = True
        self.disable()
        self.disable_timeout()

    # Método que trata o timeout da FSM.
    # Se a transmissão já foi concluída, chama o método handle_fim.
    # Se o último pacote foi enviado, reenvia ele para o servidor e reativa o timeout.
    def handle_timeout(self):
        if self.terminado:
            self.handle_fim()
            return
        
        elif self.last_packet_sent:
            print("FEM: Timeout detectado. Reenviando último pacote.")
            data = TFTP2_ProtoPacket.to_bytes(self.last_packet_sent)
            self.client.sock.sendto(data, self.remote_tid)
            self.enable_timeout()