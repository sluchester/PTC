import socket
from tftp.TFTPFsmRx import FEMRecepcao as TFTPFsmRx
from tftp.TFTPFsmTx import FEMTransmissao as TFTPFsmTx
from pypoller import poller

class TFTPClient:
    'Cliente TFTP que permite enviar e receber arquivos usando FSMs (Máquinas de Estados Finitos).'
    # Inicializa o cliente TFTP com o IP do servidor, porta e timeout.
    # O timeout é o tempo máximo de espera para receber uma resposta do servidor.
    # O socket UDP é criado e configurado com o timeout especificado.
    # O socket é usado para enviar e receber pacotes TFTP.
    def __init__(self, server_ip, server_port, timeout=5):
        self.server_ip = server_ip
        self.server_port = server_port
        self.timeout = timeout
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(self.timeout)

    # Envia um arquivo para o servidor TFTP usando uma máquina de estados finita (FSM).
    # O método TFTPFsmTx é usado para gerenciar a transmissão do arquivo.
    # Ele cria um agendador (scheduler) que adiciona a FSM de transmissão e despacha as tarefas.
    # O agendador processa os eventos e gerencia o estado da transmissão.
    # Após a conclusão, o agendador encerra a transmissão e libera os recursos.
    # Recebe um nome de arquivo como parâmetro, que é o arquivo a ser enviado.
    # O arquivo deve existir no sistema de arquivos local.
    def send_file(self, filename):
        print("Cliente: Enviando arquivo com FSM...")
        sched = poller.Poller()
        fsmTx = TFTPFsmTx(self, filename, timeout=self.timeout)
        sched.adiciona(fsmTx)
        sched.despache()

    # Recebe um arquivo do servidor TFTP usando uma máquina de estados finita (FSM).
    # O método TFTPFsmRx é usado para gerenciar a recepção do arquivo.
    # Ele cria um agendador (scheduler) que adiciona a FSM de recepção e despacha as tarefas.
    # O agendador processa os eventos e gerencia o estado da recepção.
    # Após a conclusão, o agendador encerra a recepção e libera os recursos.
    # Recebe um nome de arquivo como parâmetro, que é o arquivo a ser recebido.
    # O arquivo será salvo no sistema de arquivos local com o nome especificado.
    # Se o arquivo já existir, ele será sobrescrito.
    # O timeout é usado para definir o tempo máximo de espera para receber pacotes do servidor.
    def receive_file(self, filename):
        print("Cliente: Recebendo arquivo com FSM...")
        sched = poller.Poller()
        fsmRx = TFTPFsmRx(self, filename, timeout=self.timeout)
        sched.adiciona(fsmRx)
        sched.despache()

    # Fecha o socket UDP usado pelo cliente TFTP.
    # Libera os recursos do sistema associados ao socket.
    def close(self):
        self.sock.close()