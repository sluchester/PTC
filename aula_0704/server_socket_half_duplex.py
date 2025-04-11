from socket import *
import sys, termios

HOST = '127.0.0.1'  # Endereço IP local
PORT = 12345        # Porta para escutar

with socket(AF_INET, SOCK_STREAM) as serverSocket:
    serverSocket.bind((HOST, PORT))
    serverSocket.listen(1)
    print(f"[SERVIDOR] Aguardando conexão em {HOST}:{PORT}...")

    conn, addr = serverSocket.accept()
    with conn:
        print(f"[SERVIDOR] Conectado por {addr}")

        try:
            while True:
                # Recebe mensagem do cliente
                data = conn.recv(1024)
                if not data:
                    print("[SERVIDOR] Cliente desconectado.")
                    break
                print(f"cliente: {data.decode()}")

                # Envia mensagem para o cliente
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
                msg = input("servidor: ")
                if msg.lower() == 'sair':
                    break
                conn.sendall(msg.encode())

        finally:
            print("[SERVIDOR] Conexão encerrada.")
