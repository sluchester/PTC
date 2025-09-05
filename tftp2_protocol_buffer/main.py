import sys
from tftplus.TFTPlus_Client import TFTPlus_Client

# Lê a linha de comando para determinar a operação (enviar ou receber), o arquivo, o IP e a porta do servidor.
# Cria uma instância do cliente TFTP e executa a operação solicitada.
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Uso: python3 main.py [send|recv] arquivo ip porta")
        sys.exit(1)

    operacao, arquivo, ip, porta = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])

    client = TFTPlus_Client(ip, porta)

    if operacao == "send":
        client.send_file(arquivo)
    elif operacao == "recv":
        client.receive_file(arquivo)
    else:
        print("Operação inválida. Use 'send' ou 'recv'.")

    client.close()