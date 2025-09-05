#!/usr/bin/python3

from serial import Serial
import sys

try:
    porta = sys.argv[1]
except:
    print('Uso: %s porta_serial' % sys.argv[0])
    sys.exit(1)

try:
    p = Serial(porta, 9600, timeout=1)
except Exception as e:
    print('Não conseguiu acessar a porta serial:', e)
    sys.exit(1)

print("Receptor iniciado. Aguardando mensagens... (Ctrl+C para parar)")

try:
    while True:
        msg = p.readline().decode('ascii', errors='ignore').strip()
        if msg:
            print(f"Recebido: {msg}")
except KeyboardInterrupt:
    print("\nReceptor finalizado pelo usuário.")
finally:
    p.close()