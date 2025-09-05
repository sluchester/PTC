# Realiza a importação de módulos necessários para construir os pacotes TFTP2 
    # e gerenciar a máquina de estados.
# Importa a classe TFTP2_ProtoPacket para manipulação de pacotes TFTP2,
    # e a classe poller.Callback para gerenciar eventos de recepção de dados.
from enum import Enum, auto
from tftplus.TFTPlus_ProtoPacket import TFTP2_ProtoPacket
from pypoller import poller

# Enum que define os estados possíveis da FSM de transmissão
class EstadoRx(Enum):
    INIT = auto()
    RX = auto()
    FIM = auto()
    ERRO = auto()

# Classe principal da máquina de estados de recepção (FSM RX)
# Herda de poller.Callback para poder ser usada no poller (event loop)
# Gerencia a recepção de pacotes TFTP2 e grava os dados recebidos em um arquivo
# Inicia com o estado INIT e espera receber pacotes DATA do servidor
# Transita entre os estados RX, FIM e ERRO conforme os pacotes recebidos
# Utiliza a classe TFTP2_ProtoPacket para manipular os pacotes TFTP2
class TFTPlus_FsmRx(poller.Callback):
    def __init__(self, client, filename=None, timeout=5):
        if not filename:
            raise ValueError("O nome do arquivo deve ser fornecido.")

        super().__init__(client.sock, timeout)  # Inicializa a classe base do poller com socket e timeout
        self.client = client    # Referência ao cliente (usa IP, porta e socket)
        self.filename = filename    # Nome do arquivo a ser recebido
        self.state = EstadoRx.INIT  # Estado inicial da FSM
        self.block_number = 1   # Número do bloco atual (começa em 1)
        self.terminado = False  # Flag para indicar se a recepção foi concluída
        self.remote_tid = (self.client.server_ip, self.client.server_port)  # TID remoto (IP e porta do servidor)

    # O método start envia o pacote RRQ (Read Request) para o servidor
        # solicitando o arquivo especificado pelo nome
    # Monta e seriliza o pacote RRQ a partir da classe TFTP2_ProtoPacket
    # Habilita o timeout para retransmissão em caso de falha
    def start(self):
        msg = TFTP2_ProtoPacket.criar_rrq(self.filename)
        data = TFTP2_ProtoPacket.to_bytes(msg)
        self.client.sock.sendto(data, self.remote_tid)
        self.enable_timeout()
        print(f"FEM: RRQ enviado para {self.remote_tid}")

    # Método chamado pelo poller quando há dados disponíveis no socket
    # Recebe os dados, converte para mensagem protobuf e chama a máquina de estados (mef)
    # Se a recepção foi concluída, desabilita o poller e o timeout
    # Se ocorrer um erro, transita para o estado ERRO
    def handle(self):
        if self.terminado:
            self.disable()
            self.disable_timeout()
            print("FEM: Recepção concluída.")
            return
        try:
            data, addr = self.fd.recvfrom(1024)  # type: ignore
            msg = TFTP2_ProtoPacket.from_bytes(data)
            self.recebido = (msg, addr)
            self.mef()
        except Exception as e:
            print(f"FEM: Erro no handle(): {e}")
            self._erro()

    # Método que processa o estado atual da FSM.
    # Chama o método específico para o estado atual (INIT, RX, FIM, ERRO)
    # Cada método de estado possui uma lógica específica (handle) para aquele estado
    def mef(self):
        if self.state == EstadoRx.INIT:
            self.handle_init()
        elif self.state == EstadoRx.RX:
            self.handle_rx()
        elif self.state == EstadoRx.FIM:
            self.handle_fim()
        elif self.state == EstadoRx.ERRO:
            self.handle_erro()

    # Método que lida com o estado INIT da FSM.
    # Espera receber o primeiro pacote DATA do servidor.
    # Se o pacote DATA for recebido corretamente, grava o bloco no arquivo,
        # envia um ACK e transita para o estado RX.
    # Se o pacote DATA for o último (menor que 512 bytes), transita para o estado FIM
        # e define a flag de término como True.
    # Se um pacote de erro for recebido, transita para o estado ERRO.
    # Se um pacote inesperado for recebido, imprime uma mensagem de erro.
    def handle_init(self):
        msg, addr = self.recebido
        if TFTP2_ProtoPacket.tipo(msg) == "DATA" and msg.data.block_n == self.block_number:
            self.remote_tid = addr
            self._gravar_bloco(msg.data.message)
            self._enviar_ack(msg.data.block_n)
            if len(msg.data.message) < 512:
                print("FEM[INIT]: Último bloco. Indo para FIM.")
                self.state = EstadoRx.FIM
                self.terminado = True
                return
            else:
                self.block_number += 1
                self.state = EstadoRx.RX
        elif TFTP2_ProtoPacket.tipo(msg) == "ERROR":
            print(f"FEM[INIT]: Erro recebido: {msg.error.errormsg}")
            self._erro()
        else:
            print("FEM[INIT]: Pacote inesperado.")

    # Método que lida com o estado RX da FSM.
    # Recebe pacotes DATA do servidor, verifica se o bloco recebido é o esperado.
    # Se for, grava o bloco no arquivo, envia um ACK e incrementa o número do bloco.
    # Se o ACK for para o último bloco, transita para o estado FIM.
    # Se um pacote de erro for recebido, transita para o estado ERRO.
    def handle_rx(self):
        msg, addr = self.recebido
        if addr != self.remote_tid:
            print(f"FEM[RX]: TID inválido: esperado {self.remote_tid}, recebido {addr}")
            self._erro()
            return
        if TFTP2_ProtoPacket.tipo(msg) == "DATA" and msg.data.block_n == self.block_number:
            self._gravar_bloco(msg.data.message)
            self._enviar_ack(msg.data.block_n)
            if len(msg.data.message) < 512:
                print("FEM[RX]: Último bloco. Indo para FIM.")
                self.state = EstadoRx.FIM
                self.terminado = True
            else:
                self.block_number += 1
        elif TFTP2_ProtoPacket.tipo(msg) == "ERROR":
            print(f"FEM[RX]: Erro recebido: {msg.error.errormsg}")
            self._erro()

    # Método que lida com o estado FIM da FSM.
    # Desabilita a FSM e o timeout, indicando que a transmissão foi concluída.
    # Imprime mensagem de conclusão.
    def handle_fim(self):
        self.disable()
        self.disable_timeout()
        print("FEM[FIM]: Recepção finalizada com sucesso.")

    # Método que lida com o estado ERRO da FSM.
    # Imprime mensagem de erro, desabilita a FSM e o timeout.
    # Define a flag de término como True.
    def handle_erro(self):
        print("FEM[ERRO]: Recepção abortada por erro.")
        self.terminado = True
        self.disable()
        self.disable_timeout()

    # Método que grava o bloco de dados recebido no arquivo.
    # Se for o primeiro bloco, abre o arquivo em modo de escrita.
    # Se for um bloco subsequente, abre em modo de anexação.
    def _gravar_bloco(self, dados):
        modo = 'ab' if self.block_number > 1 else 'wb'
        with open(self.filename, modo) as f:
            f.write(dados)

    # Método que envia o ACK para o servidor.
    # Monta o pacote ACK a partir da classe TFTP2_ProtoPacket e envia
        # para o endereço remoto (remote_tid).
    # Imprime mensagem de confirmação do envio do ACK.
    def _enviar_ack(self, bloco):
        msg = TFTP2_ProtoPacket.criar_ack(bloco)
        data = TFTP2_ProtoPacket.to_bytes(msg)
        self.client.sock.sendto(data, self.remote_tid)
        print(f"FEM: ACK {bloco} enviado para {self.remote_tid}")

    # Método que trata erros de recepção.
    # Define o estado como ERRO, desabilita a FSM e o timeout,
        # e define a flag de término como True.
    def _erro(self):
        print("FEM: Entrando no estado de erro.")
        self.state = EstadoRx.ERRO
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
        
        else:
            print("FEM: Timeout detectado. Nenhum pacote recebido.")
            self._erro()