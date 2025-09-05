import sys
from Subcamada import Subcamada
from Quadro import Quadro

class Adaptacao(Subcamada):
    'lê e apresenta sequências de caracteres por meio do terminal'
    'lê alguns caracteres do terminal, e os envia para o enquadramento'
    
    def __init__(self):
       Subcamada.__init__(self, sys.stdin, 0)
       self.disable_timeout()
       print('>', end='', flush=True)
  
    def handle(self):
      # lê uma linha do teclado
      linha = sys.stdin.readline()

      # converte para bytes ... necessário somente
      # nesta aplicação de teste, que lê do terminal
      quadro = Quadro()
      quadro.defineIdProto(0)
      quadro.defineIdPayload(linha.encode())

      # envia os dados para a subcamada inferior (self.lower)
      self.lower.envia(quadro)
      print('>', end='', flush=True)

    def recebe(self, quadro:Quadro):
      'mostra na tela os dados recebidos da subcamada inferior'
      dados = quadro.payload()
      print('RX:', dados.decode())