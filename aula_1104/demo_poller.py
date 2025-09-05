from poller import Poller, Callback
import socket
import sys

class CbIn(Callback):
  'Um Callback que espera algo do teclado, e envia por um socket UDP'

  def __init__(self, sock:socket, dest:tuple):
    Callback.__init__(self, sys.stdin, 0)
    self.disable_timeout()
    self._sock = sock
    self._dest = dest

  def handle(self):
    msg = sys.stdin.readline()
    self._sock.sendto(msg.encode(), dest)


class CbSock(Callback):
  'Um Callback que espera algo do socket, e mostra na tela o que foi recebido'

  def __init__(self, sock:socket):
    Callback.__init__(self, sock, 0)
    self.disable_timeout()

  def handle(self):
    # o descritor monitorado fica no atributo fd do Callback
    msg, addr = self.fd.recvfrom(1024)
    print(f'RX {addr[0]}:{addr[1]}: {msg.decode()}')

# if len(sys.argv) < 4:
#   print(f"Uso:  ")

try:
  dest = (sys.argv[2], int(sys.argv[3]))
except:
  print(f'Uso: {sys.argv[0]} host port')
  sys.exit(0)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# faz este socket usar o portg 5678 ... mas poderia ser qualquer outro !
sock.bind(('127.0.0.1', int(sys.argv[1])))

cb1 = CbIn(sock, dest)
cb2 = CbSock(sock)
sched = Poller()
sched.adiciona(cb1)
sched.adiciona(cb2)

sched.despache()