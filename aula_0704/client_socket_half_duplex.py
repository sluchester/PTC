from socket import *
import sys, termios

HOST = '127.0.0.1'  # The server's hostname or IP address

# print('Digite uma porta acima de 1024')
PORT = 12345 # Port to listen on (non-privileged ports are > 1023)

with socket(AF_INET, SOCK_STREAM) as clientSocket:
    clientSocket.connect((HOST, PORT))
    print(f"[CLIENTE] Conectado ao servidor em {HOST}:{PORT}")
    
    # Enviando mensagens
    try:
        while True:
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
            msg = input("cliente: ")
            if msg.lower() == 'sair':
                break
            clientSocket.sendall(msg.encode())
            resposta = clientSocket.recv(1024)
            print(f"servidor: {resposta.decode()}")
    finally:
        clientSocket.close()
        print("[CLIENTE] Conexão encerrada.")