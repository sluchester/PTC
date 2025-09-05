# criado um .venv através de 
    # python3 -m venv .asn1   
# source .asn1/bin/activate.fish 

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

def receber(clientSocket):
    while True:
        try:
            # pode receber até 1024 bytes
            data = clientSocket.recv(1024)
            if not data:
                print("\n[CLIENTE] Servidor desconectado.")
                break
            
            # Decodifica a mensagem
            msg = spec.decode('Mensagem', data) 
            # ao receber um dado, decodifica de bytes para string
            print(f"\n[RECEBIDO do SERVIDOR]: {msg}")
            # open('msg.dataServer','wb').write(msg)
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
            # Codifica a mensagem
            data = spec.encode('Mensagem', string_para_asn1(msg))
            # codifica a mensagem digitada em bytes para enviar
            clientSocket.sendall(data)
            # Grava a mensagem em um arquivo
            #open('msg.dataServer','wb').write(data)
            print(f"[ENVIADO para SERVIDOR]: {data}")
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