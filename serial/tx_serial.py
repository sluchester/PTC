#!/usr/bin/python3

from serial import Serial
import sys

try:
    porta = sys.argv[1]
except:
    print('Uso: %s porta_serial' % sys.argv[0])
    sys.exit(1)

try:
    p = Serial(porta, 9600, timeout=2)
except Exception as e:
    print('Não conseguiu acessar a porta serial:', e)
    sys.exit(1)

print("Digite mensagens para enviar. Digite 'exit' para sair.")
while True:
    mensagem = input('> ')
    if mensagem.lower() == 'exit':
        break
    p.write((mensagem + '\n').encode('ascii'))
    print(f"Enviado: {mensagem}")

p.close()
print("Transmissor finalizado.")
