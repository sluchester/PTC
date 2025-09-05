import asn1tools
from socket import *
import threading
from pyasn1.type import univ

HOST = '127.0.0.1'
PORT = 12345

# compila a especificação
spec = asn1tools.compile_files('msg.asn1', codec='der')

def string_para_asn1(texto):
  """
  Converte uma string Python para o tipo IA5String do padrão ASN.1.
  Args:
    texto: A string a ser convertida.
  Returns:
    Um objeto IA5String representando a string no padrão ASN.1.
  """
  return univ.IA5String(texto.encode('utf-8'))

# recebe mensagem do cliente
def receber(conn):
    while True:
        try:
            # pode receber até 1024 bytes
            data = conn.recv(1024)
            if not data:
                print("\n[SERVIDOR] Cliente desconectado.")
                break
            # Decodifica a mensagem
            msg = spec.decode('Mensagem', data) 
            # ao receber um dado, decodifica de bytes para string
            print(f"\n[RECEBIDO do CLIENTE]: {msg}")
            # open('msg.dataClient','wb').write(msg)
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
            # Codifica a mensagem
            data = spec.encode('Mensagem', string_para_asn1(msg))
            # codifica a mensagem digitada em bytes para enviar
            conn.sendall(data)
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