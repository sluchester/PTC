from Subcamada import Subcamada
from FsmEnq import FsmEnq, FLAG
import time

class Enquadramento(Subcamada):
    """
    Enquadramento: subcamada responsável por:
    - Fazer stuffing/destuffing
    - Delimitar quadros com FLAG
    - Controlar timeout durante recepção de quadros
    Herda de Subcamada → que herda de Callback (pypoller)
    """

    def __init__(self, porta_serial, tout=0.5):
        """
        porta_serial: instância de serial.Serial (ou SerialFake)
        tout: timeout em segundos
        """
        super().__init__(porta_serial, tout)
        self.disable_timeout()  # desativa timeout por padrão
        self.dev = porta_serial
        self.tout = tout
        self.poller = None  # será configurado no main com conecta_poller()

        # Cria FSM, passando:
        # - self.handle_fsm_timeout: função que ativa/desativa timer
        # - self.recebe_quadro: função chamada ao receber quadro completo
        self.fsm = FsmEnq(self.handle_fsm_timeout, self.recebe_quadro)

    def conecta_poller(self, poller):
        """Armazena referência ao poller"""
        self.poller = poller

    def handle(self):
        """
        Chamado pelo poller quando há dados na serial.
        Lê um byte e envia para FSM.
        """
        # n = self.dev.in_waiting if hasattr(self.dev, 'in_waiting') else 1
        # dados = self.dev.read(n)
        # for b in dados:
        #     self.fsm.input_byte(b)
        octeto = self.dev.read(1)
        if octeto:
            byte = octeto[0]
            print(f"[ENQ] {time.time():.3f}: Byte recebido: {byte:02X}")
            self.fsm.input_byte(byte)

    def handle_timeout(self):
        """
        Chamado pelo poller quando o timeout estoura.
        Notifica a FSM para descartar quadro atual.
        """
        print("[Enquadramento] Timeout detectado pelo poller")
        self.fsm.timeout()

    def envia(self, dados: bytes):
        """
        Recebe dados da camada superior, faz stuffing e envia para serial.
        """
        quadro = bytearray()
        quadro.append(FLAG)
        quadro.append(FLAG)

        for byte in dados:
            if byte in (FLAG, 0x7D):
                quadro.append(0x7D)
                quadro.append(byte ^ 0x20)
            else:
                quadro.append(byte)

        quadro.append(FLAG)

        self.dev.write(bytes([FLAG]))
        self.dev.write(quadro)
        print(f"[Enquadramento] Quadro enviado: {list(quadro)}")

    def recebe_quadro(self, quadro: bytes):
        """
        Chamado pela FSM quando um quadro completo é recebido.
        Passa para camada superior.
        """
        print(f"[Enquadramento] Quadro completo recebido: {list(quadro)}")
        if self.upper:
            self.upper.recebe(quadro)

    def handle_fsm_timeout(self, ligar: bool):
        """
        Função passada para FSM:
        - Se ligar=True → ativa/reinicia timeout
        - Se ligar=False → desativa timeout
        """
        if ligar:
            self.base_timeout = self.tout
            self.reload_timeout()
            self.enable_timeout()
        else:
            self.disable_timeout()