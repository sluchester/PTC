import time
from serial import Serial
from Subcamada import Subcamada

class Enquadramento(Subcamada):
    'O enquadramento envia e recebe quadros pela porta serial'
    'o enquadramento encapsula os caracteres em um quadro e envia pela porta serial.'
    
    def __init__(self, porta_serial:Serial, tout:float):
      Subcamada.__init__(self, porta_serial, tout)
      # dev: este atributo mantém uma referência à porta serial
      self.dev = porta_serial
      # buffer: este atributo armazena octetos recebidos
      self.buffer = bytearray()

    def handle(self):
      # lê um octeto da serial, e o armazena no buffer
      # Encaminha o buffer para camada superior, se ele tiver 8 octetos
        # criar a maquina de estados aqui para processar isso
      octeto = self.dev.read(1)
      self.buffer += octeto
      
      if len(self.buffer) == 8:
        # envia o conteúdo do buffer para a camada superior (self.upper)
        if self.upper is not None:
          self.upper.recebe(bytes(self.buffer))
          print('Enviando quadro para camada superior:', bytes(self.buffer))
        self.buffer.clear()        
        
    def handle_timeout(self):
      # Limpa o buffer se ocorrer timeout
      self.buffer.clear()
      print('timeout no enquadramento em', time.time())

    def envia(self, dados:bytes):
      # Apenas envia os dados pela serial
      # Este método é chamado pela subcamada superior
      quadro = bytearray()
      quadro.append(0x7e)
      quadro += dados
      quadro.append(0x7e)
      self.dev.write(bytes(quadro))