from socket import *

# cria um socket TCP
# Usa a primitiva "socket"
sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)

# Associa um endereço e port a este socket: qualquer IP usado
# neste host, e um port livre à escolha do sistema operacional
# Usa a primitiva "bind"
sock.bind(('0.0.0.0', 0))

# Estabelece uma conexão com o servidor www.sj.ifsc.edu.br, no port 80
# Usa a primitiva "connect"
sock.connect(('www.sj.ifsc.edu.br', 80))

# Cria algum conteúdo a ser enviado ao servidor
msg = '''GET / HTTP/1.0
Host: www.sj.ifsc.edu.br

'''

# envia o conteúdo para o servidor
# Usa a primitiva "send"
sock.send(msg.encode())

# Recebe algum conteúdo do servidor
# Usa a primitiva "recv"
# Pode receber até 1024 bytes
data = sock.recv(1024)

# Mostra o conteúdo na saída padrão
print(data.decode())

# Encerra a conexão
# Usa a primitiva "shutdown"
sock.shutdown(SHUT_RDWR)