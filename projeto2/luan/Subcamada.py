from pypoller.poller import Callback
from typing import Optional

class Subcamada(Callback):
    def __init__(self, *args):
        Callback.__init__(self,*args)
        self.upper: Optional[Subcamada] = None
        # self.lower = None
        self.lower: Optional[Subcamada] = None

    def envia(self, dados):
        raise NotImplementedError('abstrato')
    
    def recebe(self, dados):
        raise NotImplementedError('abstrato')
    
    def conecta(self, acima):
        self.upper = acima
        # self.lower = self #redundante, mas pode ser útil