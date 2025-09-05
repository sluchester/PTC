from enum import Enum, auto

FLAG = 0x7E
ESCAPE = 0x7D
XOR_MASK = 0x20
MAX_LEN = 256

class State(Enum):
    OCIOSO = auto()
    RX = auto()
    ESCAPE = auto()

class FsmEnq:
    def __init__(self, timeout_handler, on_frame_callback):
        """
        timeout_handler: função que liga (True) ou desliga (False) o timer
        on_frame_callback: função chamada ao receber quadro completo
        """
        self.state = State.OCIOSO
        self.buffer = []
        self.fsm_timeout_handler = timeout_handler
        self.on_frame_callback = on_frame_callback

    def reset(self):
        """Reinicia FSM: volta para OCIOSO e limpa buffer"""
        print("[FSM] Reset: voltando para OCIOSO")
        self.state = State.OCIOSO
        self.fsm_timeout_handler(False)  # desativa timeout
        self.buffer.clear()

    def input_byte(self, byte):
        """Recebe um byte e despacha para o handler do estado atual"""
        match self.state:
            case State.OCIOSO:
                self.ocioso_handler(byte)
            case State.RX:
                self.rx_handler(byte)
            case State.ESCAPE:
                self.escape_handler(byte)

    def ocioso_handler(self, byte):
        if byte == FLAG:
            print("[FSM] FLAG recebida: iniciando recepção de quadro")
            self.buffer.clear()
            self.state = State.RX
            self.fsm_timeout_handler(True)  # ativa timeout
        # outros bytes são ignorados
        # else :
        #     self.state = State.OCIOSO

    def rx_handler(self, byte):
        if byte == FLAG:
            # fim do quadro
            print(f"[FSM] Quadro recebido: {self.buffer}")
            if self.on_frame_callback and len(self.buffer) > 0:
                self.on_frame_callback(bytes(self.buffer))
            self.reset()
        elif byte == ESCAPE:
            print("[FSM] ESCAPE recebido, próximo byte será processado")
            self.state = State.ESCAPE
            self.fsm_timeout_handler(True)  # renova timeout
        elif len(self.buffer) < MAX_LEN:
            self.buffer.append(byte)
            self.fsm_timeout_handler(True)  # renova timeout
        # else:
        #     print("[FSM] Erro: quadro excedeu tamanho máximo")
        #     self.reset()
        else:
            self.buffer.append(byte)
            self.fsm_timeout_handler(True)

    def escape_handler(self, byte):
        if len(self.buffer) < MAX_LEN:
            valor = byte ^ XOR_MASK
            self.buffer.append(valor)
            print(f"[FSM] Byte escapado adicionado: {valor}")
            self.state = State.RX
            self.fsm_timeout_handler(True)  # renova timeout
        else:
            print("[FSM] Erro: quadro excedeu tamanho máximo após ESCAPE")
            self.reset()

    def timeout(self):
        print("[FSM] Timeout: quadro descartado")
        self.reset()