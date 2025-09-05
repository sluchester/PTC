from pypoller import poller
from tftp.TFTPClient import TFTPClient
import sys

def main():
    'Responsável por iniciar o cliente TFTP e processar os comandos do usuário.'
    print("====== Cliente TFTP ======")
    print("Formato esperado:")
    print("  <modo> <arquivo_local> <ip> [porta]")
    print("Exemplo:")
    print("  send meu.txt 127.0.0.1 69      ou     recv meu.txt 127.0.0.1 69 ")

    # Lê os parâmetros do usuário
    entrada = input("\nDigite os parâmetros: ").strip()
    partes = entrada.split()

    # Verifica se os parâmetros são válidos
    if len(partes) < 3:
        print("Erro: parâmetros insuficientes.")
        return

    # Desempacota os parâmetros para variáveis que serão usadas na criação do cliente TFTP
    modo, filename, ip = partes[:3]
    porta = int(partes[3]) if len(partes) >= 4 else 69

    # Verifica se o modo é válido
    if modo not in ["send", "recv"]:
        print("Erro: modo deve ser 'send' ou 'recv'.")
        return

    # Cria o cliente TFTP com os parâmetros fornecidos
    client = TFTPClient(ip, porta, timeout=5)

    # Define qual método chamar com base no modo
    if modo == "send":
        client.send_file(filename)
    elif modo == "recv":
        client.receive_file(filename)

if __name__ == "__main__":
    main()
