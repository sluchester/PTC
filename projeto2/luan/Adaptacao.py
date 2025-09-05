import sys
from Subcamada import Subcamada

class Adaptacao(Subcamada):
    """
    Camada de adaptação entre stdin/stdout e a pilha de enlace.
    - No modo TX: lê do teclado e envia para baixo.
    - No modo RX: recebe dados da pilha e imprime na tela.
    """
    def __init__(self):
        # Usa sys.stdin como fileobj para o poller, sem timeout
        super().__init__(sys.stdin, 0)
        # Desativa o timer (apenas eventos de leitura)
        self.disable_timeout()
        self.lower = None
        # Prompt inicial
        print('> ', end='', flush=True)

    def handle(self):
        # Chamado pelo poller quando o usuário digita uma linha
        linha = sys.stdin.readline()
        if not linha:
            return

        dados = linha.encode('ascii', errors='ignore')
        if self.lower is not None:
            self.lower.envia(dados)

        print('> ', end='', flush=True)

    def recebe(self, dados: bytes):
        # Chamado pela pilha de enlace quando chegar um quadro decodificado
        texto = dados.decode('ascii', errors='ignore').rstrip()
        print(f"\nRX: {texto}")
        print('> ', end='', flush=True)