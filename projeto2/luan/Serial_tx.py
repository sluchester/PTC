import sys
import time
from pypoller.poller import Poller
from serial import Serial
from DeteccaoErros import DeteccaoErros
from Enquadramento import Enquadramento
from Adaptacao import Adaptacao

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
    adapt = Adaptacao()                            # camada de aplicação (stdin/stdout)
    crc   = DeteccaoErros()                        # detecção de erros (CRC-16)
    enq   = Enquadramento(porta, tout=0.5)         # enquadramento + FSM + timeout

    # Conecta pilha: Aplicacao -> CRC -> Enquadramento -> Serial
    adapt.conecta(acima=None)                      # camada superior inexistente
    crc.conecta(acima=adapt)
    enq.conecta(acima=crc)

    # Ajusta ponteiro lower
    adapt.lower = crc   #talvez tenha que tirar depois isso aqui
    crc.lower   = enq

    # Registra para receber eventos do teclado e da serial
    poller.adiciona(adapt)   # vigia stdin
    poller.adiciona(enq)      # vigia serial + timeout

    print("[TX] Transmissor pronto. Digite mensagens abaixo:")
    try:
        poller.despache()
    except KeyboardInterrupt:
        print("\n[TX] Finalizando...")
    finally:
        porta.close()