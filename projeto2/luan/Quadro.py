class Quadro:
    def __init__(self):
        #campos do cabeçalho
        self.controle = 0
        self.reservado = 0
        self.id_proto = 0
        #payload
        self.dados = b''

    def defineSequencia(self, seq:int):
        'seq: deve ser 0 ou 1'
        self.controle &= 0xf07 # reseta bit 3
        self.controle |= seq << 3 #seta bit 3 com valor de seq

    def sequencia(self)->int:
        'retorna o valor do bit 3'
        return (self.controle & 0x8) >> 3
    
    def serialize(self) -> bytes:
        'Serializa o quadro em bytes'
        buff = bytearray()
        buff.append(self.controle)
        buff.append(self.reservado)
        buff.append(self.id_proto)
        buff += self.dados
        return bytes(buff)