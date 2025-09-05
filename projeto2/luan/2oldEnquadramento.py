import time
from serial import Serial
from Subcamada import Subcamada
from FsmEnq import FsmEnq

FLAG = 0x7E
ESCAPE = 0x7D
XOR_MASK = 0x20

class Enquadramento(Subcamada):
    """
    Enquadramento: faz stuffing/destuffing, controla timeout e
        processa recepção com FSM (FsmEnq).
    Integrado ao poller via Subcamada.
    """

    def __init__(self, porta_serial: Serial, tout: float):
        super().__init__(porta_serial, tout)
        self.dev = porta_serial
        self.tout = tout  # tempo de timeout em segundos
        self.poller = None  # será configurado externamente

        # FSM para processar bytes recebidos
        self.fsm = FsmEnq(
            timeout_handler=self.handle_fsm_timeout,
            on_frame_callback=self.entrega_para_upper
        )

    def conecta_poller(self, poller):
        """
        Guarda referência ao poller, para registrar e cancelar timeouts.
        """
        self.poller = poller

    def handle(self):
        """
        Chamado pelo poller quando há dado disponível.
        Lê byte e envia para FSM.
        """
        octeto = self.dev.read(1)
        if octeto:
            byte = octeto[0]
            self.fsm.input_byte(byte)

    def handle_timeout(self):
        """
        Chamado pelo poller quando timeout expira.
        Repassa evento para FSM.
        """
        print("[Enquadramento] Timeout detectado pelo poller")
        self.fsm.timeout()

    def handle_fsm_timeout(self, ligar: bool):
        """
        Chamado pela FSM para ativar ou cancelar timeout no poller.
        """
        if ligar:
            self.set_timeout()
        else:
            self.clear_timeout()

    def set_timeout(self):
        """
        Ativa timeout no poller, se configurado.
        """
        # if self.poller:
        #     self.poller.set_timeout(self, self.tout)
        #     print(f"[Enquadramento] Timeout ativado por {self.tout} segundos")
        # else:
        #     print("[Enquadramento] Poller não configurado, não foi possível ativar timeout")
        self.base_timeout = self.tout
        self.reload_timeout()
        self.enable_timeout()

    def clear_timeout(self):
        """
        Cancela timeout no poller.
        """
        # if self.poller:
        #     self.poller.clear_timeout(self)
        #     print("[Enquadramento] Timeout cancelado")
        # else:
        #     print("[Enquadramento] Poller não configurado, não foi possível cancelar timeout")
        self.disable_timeout()

    def entrega_para_upper(self, quadro: bytes):
        """
        Callback chamado pela FSM ao receber quadro completo.
        Entrega para camada superior.
        """
        if self.upper is not None:
            print(f"[Enquadramento] Quadro entregue para camada superior: {quadro}")
            self.upper.recebe(quadro)
        else:
            print("[Enquadramento] Nenhuma camada superior conectada!")

    def envia(self, dados: bytes):
        """
        Chamado pela camada superior para enviar dados.
        Faz stuffing e adiciona flags antes de enviar.
        """
        quadro = bytearray()
        quadro.append(FLAG)

        for byte in dados:
            if byte == FLAG or byte == ESCAPE:
                quadro.append(ESCAPE)
                quadro.append(byte ^ XOR_MASK)
            else:
                quadro.append(byte)

        quadro.append(FLAG)
        self.dev.write(bytes(quadro))
        print(f"[Enquadramento] Quadro enviado na serial: {quadro}")

