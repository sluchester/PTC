#!/usr/bin/python3
import sys
from pypoller.poller import Poller
from serial import Serial
from DeteccaoErros import DeteccaoErros
from Enquadramento import Enquadramento
from Adaptacao import Adaptacao
from arq import ARQ

def main():
    if len(sys.argv) != 2:
        print(f"Uso: python3 {sys.argv[0]} <porta_serial>")
        sys.exit(1)

    porta_nome = sys.argv[1]
    try:
        porta = Serial(porta_nome, baudrate=9600, timeout=0.1)
    except Exception as e:
        print("Erro ao abrir porta serial:", e)
        sys.exit(1)

    # Cria o poller real
    poller = Poller()

    # Cria as camadas
    adapt = Adaptacao()                          # aplicação: stdin → envia e recebe
    arq = ARQ()                                  # ARQ: pare-e-espere
    crc   = DeteccaoErros()                      # detecção de erros
    enq   = Enquadramento(porta, tout=0.5)       # enquadramento + FSM + timeout

    # Conecta pilha
    adapt.conecta(acima=None)                    # topo da pilha não tem camada acima
    arq.conecta(acima=adapt)  # ARQ conecta acima (adaptação)
    crc.conecta(acima=arq)    # CRC conecta acima (ARQ)
    enq.conecta(acima=crc)

    # Ajusta lower (quem está abaixo)
    adapt.lower = arq
    arq.lower = crc
    crc.lower   = enq

    # Conecta o poller ao enquadramento
    enq.conecta_poller(poller)

    # Registra no poller
    poller.adiciona(adapt)   # monitora stdin
    poller.adiciona(enq)     # monitora serial + timeout

    print(f"[MAIN] Pilha montada. Porta serial: {porta_nome}")
    print("[MAIN] Digite mensagens para enviar. Recebidas aparecerão automaticamente.\n")
    print("> ")

    try:
        poller.despache()
    except KeyboardInterrupt:
        print("\n[MAIN] Encerrando...")
    finally:
        porta.close()

if __name__ == "__main__":
    main()
