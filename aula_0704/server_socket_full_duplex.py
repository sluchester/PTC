from socket import *
import threading

HOST = '127.0.0.1'
PORT = 12345

# recebe mensagem do cliente
def receber(conn):
    while True:
        try:
            # pode receber até 1024 bytes
            data = conn.recv(1024)
            if not data:
                print("\n[SERVIDOR] Cliente desconectado.")
                break
            # ao receber um dado, decodifica de bytes para string
            print(f"\n[RECEBIDO do CLIENTE]: {data.decode()}")
            # reexibe o prompt sem pular linha
            print("[SERVIDOR] Digite sua mensagem: ", end='', flush=True)
        except:
            break

def enviar(conn):
    while True:
        try:
            msg = input("[SERVIDOR] Digite sua mensagem: ")
            if msg.lower() == 'sair':
                print("[SERVIDOR] Encerrando conexão...")
                conn.close()
                break
            conn.sendall(msg.encode())
            print(f"[ENVIADO para CLIENTE]: {msg}")
        except:
            break

# AF_INET: tipo de endereço IP (IPv4)
# SOCK_STREAM: tipo de conexão (TCP)
with socket(AF_INET, SOCK_STREAM) as serverSocket:
    # vincula o endereço e porta
    serverSocket.bind((HOST, PORT))
    # fica esperando 1(ou n) conexão
    serverSocket.listen(1)
    print(f"[SERVIDOR] Aguardando conexão em {HOST}:{PORT}...")

    # ao aceitar a conexão, retorna conn (um canal de dados ) e addr (tupla de HOST e PORT)
    conn, addr = serverSocket.accept()
    print(f"[SERVIDOR] Conectado por {addr}")

    # cria as threads de recebeimento e envio
    thread_receber = threading.Thread(target=receber, args=(conn,))
    thread_enviar = threading.Thread(target=enviar, args=(conn,))

    # inicia as threads de recebeimento e envio
    thread_receber.start()
    thread_enviar.start()

    # espera pelo término das threads
    thread_receber.join()
    thread_enviar.join()

    print("[SERVIDOR] Conexão encerrada.")