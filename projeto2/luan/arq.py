from Subcamada import Subcamada
from collections import deque
from fsm_arq import FsmARQ

TYPE_DATA = 0x00
TYPE_ACK  = 0x01

class ARQ(Subcamada):
    """
    Subcamada ARQ pare-e-espere com fila.
    """
    def __init__(self):
        super().__init__()
        self.N = 0  # número de sequência do transmissor
        self.M = 0  # número de sequência esperado no receptor
        self.q = deque()  # fila de saída
        self.fsm = FsmARQ(self)  # FSM

    def envia(self, dados: bytes):
        """
        Chamado pela camada superior (aplicação) para enviar dado.
        """
        print(f"[ARQ] Aplicação pediu envio: {dados}")
        self.fsm.input_app_tx(dados)

    def recebe(self, dados: bytes):
        """
        Chamado pela subcamada inferior (Enquadramento) ao receber dados.
        """
        print(f"[ARQ-TX] Quadro bruto recebido: {list(dados)}")
        print(f"[ARQ] Recebeu dados da subcamada inferior: {list(dados)}")
        self.fsm.input_rx(dados)

    def handle_timeout(self):
        """
        Chamado pelo poller se houver timeout.
        """
        print("[ARQ] Timeout detectado pelo poller")
        self.fsm.handle_timeout()

    def _envia_quadro(self):
        """
        Monta e envia DATA_N.
        """
        if len(self.q) == 0:
            print("[ARQ] Aviso: tentou enviar quadro mas fila está vazia.")
            return

        dados = self.q[0]
        quadro = bytearray()
        quadro.append(TYPE_DATA)
        quadro.append(self.N)
        quadro += dados

        print(f"[ARQ] Enviando quadro DATA_{self.N}: {list(quadro)}")
        if self.lower:
            self.lower.envia(bytes(quadro))

    def _envia_ack(self, num_seq):
        """
        Monta e envia ACK.
        """
        quadro = bytearray()
        quadro.append(TYPE_ACK)
        quadro.append(num_seq)

        print(f"[ARQ] Enviando ACK_{num_seq}: {list(quadro)}")
        if self.lower:
            self.lower.envia(bytes(quadro))
