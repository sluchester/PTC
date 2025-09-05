from enum import Enum, auto
from tftp.TFTPPacket import RRQPacket, DataPacket, AckPacket, ErrorPacket, TFTPPacket
from pypoller import poller

# Declarando os estados da FSM (Finite State Machine)
# para a recepção de arquivos TFTP
# Os estados são: INIT (inicialização), RX (recepção de dados),
# FIM (finalização) e ERRO (erro de transmissão).
class State(Enum):
    INIT = auto()
    RX = auto()
    FIM = auto()
    ERRO = auto()

# Classe FEMRecepcao implementa a máquina de estados para
# a recepção de arquivos TFTP. Ela herda de poller.Callback
# para lidar com eventos de recepção de dados e timeouts.
# Ela gerencia a recepção de pacotes, gravação de blocos de dados
# e o envio de ACKs. A máquina de estados controla o fluxo
# da recepção, lidando com estados como inicialização, recepção de dados,
# finalização e erro. A classe também implementa o tratamento de timeouts
# para garantir que a recepção não fique pendente indefinidamente.
class FEMRecepcao(poller.Callback):
    def __init__(self, client, filename=None, timeout=5):
        # Verifica o fornecimento do nome do arquivo
        if not filename:
            raise ValueError("O nome do arquivo deve ser fornecido.")

        # Verifica se o cliente é uma instância de TFTPClient e seta as demais variáveis
        # para a máquina de estados trabalhar corretamente ao ser construída.
        super().__init__(client.sock, timeout)
        self.client = client
        self.filename = filename
        self.state = State.INIT
        self.block_number = 1
        self.terminado = False
        self.remote_tid = None
        self._enviar_rrq()

    # Método para enviar o pacote RRQ (Read Request)
    # para o servidor TFTP. Ele cria um pacote RRQ com o nome do arquivo
    # e o envia para o endereço do servidor TFTP.
    # O pacote RRQ é usado para solicitar a leitura de um arquivo do servidor.
    # O pacote contém o nome do arquivo e o modo de transferência ("octet").
    # O pacote é enviado via socket UDP para o servidor TFTP.
    # Após o envio, uma mensagem é impressa no console indicando que o RRQ foi enviado.
    def _enviar_rrq(self):
        pkt = RRQPacket(self.filename)
        self.client.sock.sendto(pkt.to_bytes(), (self.client.server_ip, self.client.server_port))
        print(f"FEM: RRQ enviado para {self.client.server_ip}:{self.client.server_port}")

    # Método chamado quando a máquina de estados é ativada.
    # Ele registra o callback para receber dados do socket e inicia o processo de recepção.
    def handle(self):
        if self.terminado:
            self.disable()
            self.disable_timeout()
            return
        if self.fd is None:
            return

        # Tenta receber dados do socket.
        # Se receber dados, cria um pacote TFTPPacket a partir dos bytes recebidos, 
        # armazena o pacote e o endereço remoto e chama o método mef() para processar o pacote recebido.
        
        try:
            data, addr = self.fd.recvfrom(516)
            try:
                packet = TFTPPacket.from_bytes(data)
            # Se ocorrer um erro de parsing, imprime uma mensagem de erro e entra no estado de erro.
            except ValueError as e:
                print(f"FEM: Erro de parsing: {e}")
                self._erro()
                return

            self.recebido = (packet, addr)
            self.mef()

        # Se ocorrer qualquer outra exceção, imprime uma mensagem de erro e entra no estado de erro.
        except Exception as e:
            print(f"FEM: Erro no handle(): {e}")
            self._erro()

        # Se a transferência estiver concluída, desativa a máquina de estados e o timeout
        if self.terminado:
            print("FEM: Transferência concluída.")
            self.disable()
            self.disable_timeout()

    # Método que processa o estado atual da FSM.
    # Dependendo do estado atual, chama o método apropriado para lidar com o pacote recebido
    def mef(self):
        if self.state == State.INIT:
            self.handle_init()
        elif self.state == State.RX:
            self.handle_rx()
        elif self.state == State.FIM:
            self.handle_fim()
        elif self.state == State.ERRO:
            self.handle_erro()

    # O método handle_init() lida com o estado de inicialização
    # da máquina de estados. Ele espera receber o primeiro pacote de dados (DataPacket)
    # com o número de bloco correto. Se o pacote recebido não for do tipo DataPacket
    # ou se o número do bloco não corresponder ao esperado, imprime uma mensagem de erro
    # e não faz nada. 
    def handle_init(self):
        packet, addr = self.recebido
        if isinstance(packet, DataPacket):
            if packet.block_number != self.block_number:
                print(f"FEM[INIT]: Bloco inesperado: esperado {self.block_number}, recebido {packet.block_number}")
                return
            # Se o pacote for válido, grava os dados no arquivo,
            # envia um ACK para o servidor e verifica se é o último bloco de dados.
            self.remote_tid = addr
            self._gravar_bloco(packet.data)
            self._enviar_ack(packet.block_number)
            # Se for o último bloco, muda o estado para FIM e marca a transferência como terminada.
            # Se não, incrementa o número do bloco e muda o estado para RX
            # para continuar recebendo dados.
            if len(packet.data) < 512:
                print("FEM[INIT]: Último bloco. Indo para FIM.")
                self.state = State.FIM
                self.terminado = True
            else:
                self.block_number += 1
                self.state = State.RX

    # O método handle_rx() lida com o estado de recepção de dados.
    # Ele verifica se o pacote recebido é do tipo DataPacket e se o endereço remoto
    # corresponde ao TID remoto esperado. Se o endereço remoto não corresponder 
    # ao TID remoto esperado, imprime uma mensagem de erro e entra no estado de erro.
    # Se o pacote não for do tipo DataPacket ou se o número do bloco não corresponder ao esperado,
    # imprime uma mensagem de erro e não faz nada.
    def handle_rx(self):
        packet, addr = self.recebido
        if addr != self.remote_tid:
            print(f"FEM[RX]: TID inválido: esperado {self.remote_tid}, recebido {addr}")
            self._erro()
            return
        if isinstance(packet, DataPacket):
            if packet.block_number != self.block_number:
                print(f"FEM[RX]: Bloco inesperado: esperado {self.block_number}, recebido {packet.block_number}")
                return
            # Se o pacote for válido, grava os dados no arquivo,
            # envia um ACK para o servidor e verifica se é o último bloco de dados.
            # Se for o último bloco, muda o estado para FIM e marca a transferência como terminada.
            # Se não for o último bloco, incrementa o número do bloco e continua recebendo dados.
            self._gravar_bloco(packet.data)
            self._enviar_ack(packet.block_number)
            if len(packet.data) < 512:
                print("FEM[RX]: Último bloco. Indo para FIM.")
                self.state = State.FIM
                self.terminado = True
            else:
                self.block_number += 1

    # Se a transferência for concluída, imprime uma mensagem de sucesso.
    def handle_fim(self):
        print("FEM[FIM]: Transferência finalizada com sucesso.")

     # Se ocorrer qualquer anormalidade, o estado de erro imprime uma mensagem de erro.
    def handle_erro(self):
        print("FEM[ERRO]: Transferência abortada por erro.")

    # Método para enviar um ACK (Acknowledgment) para o servidor TFTP.
    # O ACK confirma o recebimento de um bloco de dados.
    # Ele cria um pacote ACK com o número do bloco recebido e o envia para o endereço remoto.
    def _enviar_ack(self, bloco):
        pkt = AckPacket(bloco)
        self.client.sock.sendto(pkt.to_bytes(), self.remote_tid)
        print(f"FEM: ACK {bloco} enviado para {self.remote_tid}")

    # Método para gravar um bloco de dados no arquivo.
    # Se for o primeiro bloco, abre o arquivo em modo de escrita (wb),
    # caso contrário, abre em modo de anexação (ab).
    # Os dados são gravados no arquivo, e o arquivo é fechado após a gravação
    def _gravar_bloco(self, dados):
        modo = 'ab' if self.block_number > 1 else 'wb'
        with open(self.filename, modo) as f:
            f.write(dados)

    # Método para entrar no estado de erro.
    # Ele imprime uma mensagem de erro, muda o estado para ERRO,
    # marca a transferência como terminada, desativa a máquina de estados
    # e desativa o timeout.
    def _erro(self):
        print("FEM: Entrando no estado de erro.")
        self.state = State.ERRO
        self.terminado = True
        self.disable()
        self.disable_timeout()

    # Método para lidar com timeouts.
    # Ele imprime uma mensagem de timeout detectado e chama o método _erro()
    # para entrar no estado de erro.
    # O timeout é usado para evitar que a recepção fique em loop quando há um mau comportamente.
    # Se um timeout ocorrer, a máquina de estados entra no estado de erro.
    def handle_timeout(self):
        print("FEM: Timeout detectado.")
        self._erro()
