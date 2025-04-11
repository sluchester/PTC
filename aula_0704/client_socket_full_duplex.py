from socket import *
import threading

HOST = '127.0.0.1'
PORT = 12345

def receber(clientSocket):
    while True:
        try:
            # pode receber até 1024 bytes
            data = clientSocket.recv(1024)
            if not data:
                print("\n[CLIENTE] Servidor desconectado.")
                break
            # ao receber um dado, decodifica de bytes para string
            print(f"\n[RECEBIDO do SERVIDOR]: {data.decode()}")
            # reexibe o prompt sem pular linha
            print("[CLIENTE] Digite sua mensagem: ", end='', flush=True)
        except:
            break

def enviar(clientSocket):
    while True:
        try:
            msg = input("[CLIENTE] Digite sua mensagem: ")
            if msg.lower() == 'sair':
                print("[CLIENTE] Encerrando conexão...")
                clientSocket.close()
                break
            # codifica a mensagem digitada em bytes para enviar
            clientSocket.sendall(msg.encode())
            print(f"[ENVIADO para SERVIDOR]: {msg}")
        except:
            break

# AF_INET: tipo de endereço IP (IPv4)
# SOCK_STREAM: tipo de conexão (TCP)
with socket(AF_INET, SOCK_STREAM) as clientSocket:

    # espera até a conexão completar
    # se não der, retorna um TimeoutError ou InterruptedError
    clientSocket.connect((HOST, PORT))
    print(f"[CLIENTE] Conectado ao servidor em {HOST}:{PORT}")

    #cria a thread para receber e para enviar
    thread_receber = threading.Thread(target=receber, args=(clientSocket,))
    thread_enviar = threading.Thread(target=enviar, args=(clientSocket,))

    # inicia as threads
    thread_receber.start()
    thread_enviar.start()

    # espera a thread terminar
    thread_receber.join()
    thread_enviar.join()

    print("[CLIENTE] Conexão encerrada.")