from enum import Enum, auto

TYPE_DATA = 0x00
TYPE_ACK  = 0x01

class State(Enum):
    OCIOSO = auto()
    ESPERA = auto()

class FsmARQ:
    """
    FSM do ARQ pare-e-espere com fila.
    Controla estados e transições.
    """
    def __init__(self, arq):
        """
        arq: referência para a instância da classe ARQ principal.
        """
        self.arq = arq
        self.state = State.OCIOSO

    def input_app_tx(self, dados: bytes):
        """
        Evento: aplicação envia dado.
        """
        self.arq.q.append(dados)
        print(f"[FSM] App_tx chegou: {dados}")

        match self.state:
            case State.OCIOSO:
                self.arq._envia_quadro()
                self.state = State.ESPERA
                print("[FSM] Transição OCIOSO -> ESPERA")

            case State.ESPERA:
                print("[FSM] Em ESPERA: só enfileirou, não envia agora.")

    def input_rx(self, quadro: bytes):
        """
        Evento: recebe quadro da subcamada inferior.
        """
        tipo = quadro[0]
        num_seq = quadro[1]

        match self.state:
            case State.OCIOSO:
                self.ocioso_handler(tipo, num_seq, quadro)
            case State.ESPERA:
                self.espera_handler(tipo, num_seq, quadro)

    def ocioso_handler(self, tipo, num_seq, quadro):
        if tipo == TYPE_DATA:
            print(f"[FSM] OCIOSO: recebeu DATA_{num_seq}")
            if num_seq == self.arq.M:
                payload = quadro[2:]
                if self.arq.upper:
                    self.arq.upper.recebe(payload)
                self.arq._envia_ack(self.arq.M)
                self.arq.M = 1 - self.arq.M
            else:
                print("[FSM] OCIOSO: quadro duplicado, reenvia ACK")
                self.arq._envia_ack(self.arq.M)

        elif tipo == TYPE_ACK:
            print("[FSM] OCIOSO: ignorou ACK recebido (não esperava nada)")

    def espera_handler(self, tipo, num_seq, quadro):
        if tipo == TYPE_ACK:
            print(f"[FSM] ESPERA: recebeu ACK_{num_seq}")
            if num_seq == self.arq.N:
                self.arq.q.popleft()
                self.arq.N = 1 - self.arq.N
                if len(self.arq.q) > 0:
                    self.arq._envia_quadro()
                else:
                    print("[FSM] Fila vazia: ESPERA -> OCIOSO")
                    self.state = State.OCIOSO
            else:
                print("[FSM] ESPERA: ACK duplicado ou inesperado, ignorado")

        elif tipo == TYPE_DATA:
            print(f"[FSM] ESPERA: recebeu DATA_{num_seq}")
            if num_seq == self.arq.M:
                payload = quadro[2:]
                if self.arq.upper:
                    self.arq.upper.recebe(payload)
                self.arq._envia_ack(self.arq.M)
                self.arq.M = 1 - self.arq.M
            else:
                print("[FSM] ESPERA: quadro duplicado, reenvia ACK")
                self.arq._envia_ack(self.arq.M)

    def handle_timeout(self):
        """
        Evento: timeout.
        """
        print("[FSM] Timeout no estado ESPERA: retransmite quadro")
        if self.state == State.ESPERA and len(self.arq.q) > 0:
            self.arq._envia_quadro()