import sys
import time
from pypoller.poller import Poller
from serial import Serial
from DeteccaoErros import DeteccaoErros
from Enquadramento import Enquadramento

class Receptor:
    """
    Camada superior apenas imprimir os dados recebidos.
    """
    def recebe(self, dados: bytes):
        texto = dados.decode('ascii', errors='ignore').rstrip()
        print(f"RX: {texto}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Uso: {sys.argv[0]} <porta_serial>")
        sys.exit(1)

    porta_nome = sys.argv[1]
    try:
        porta = Serial(porta_nome, baudrate=9600, timeout=0.1)
    except Exception as e:
        print('Erro ao abrir porta serial:', e)
        sys.exit(1)

    # Instancia o poller
    poller = Poller()

    # Camadas do protocolo
    receptor = Receptor()                          # camada de aplicação que printa
    crc       = DeteccaoErros()                    # detecção de erros
    enq       = Enquadramento(porta, tout=0.5)     # enquadramento + FSM + timeout

    # Conecta pilha: Receptor -> CRC -> Enquadramento -> Serial
    crc.conecta(acima=receptor)
    enq.conecta(acima=crc)

    # Ajusta ponteiro lower
    crc.lower = enq

    # Registra no poller
    poller.adiciona(enq)

    print("[RX] Receptor iniciado. Aguardando mensagens...")
    try:
        poller.despache()
    except KeyboardInterrupt:
        print("\n[RX] Finalizando...")
    finally:
        porta.close()