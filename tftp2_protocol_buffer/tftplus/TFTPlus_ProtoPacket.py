# Importa a classe Mensagem gerada pelo protobuf (tftp2.proto), os quais definem os pacotes do protocolo TFTP2.
# Esta importação é necessária para que a classe TFTP2_ProtoPacket possa criar e manipular pacotes TFTP2.
# Tive que colocar o "#type ignore" porque o compilador do python estava reclamando 
    # que não conhecia a classe Mensagem
from tftplus.tftp2_pb2 import Mensagem # type: ignore

# Classe que define os pacotes do protocolo TFTP2.
# Esta classe contém métodos para criar pacotes de requisição, resposta, dados e erro.
class TFTP2_ProtoPacket:
    # Monta um pacote RRQ (Read Request) recebido do servidor TFTP2 em formato ProtoBuffer
    # quando o cliente quer receber um arquivo do servidor.
    @staticmethod
    def criar_rrq(filename):
        msg = Mensagem() # type: ignore
        msg.rrq.fname = filename
        msg.rrq.mode = 2 # Define o modo de transferência (2 = octet, conforme definido no .proto)
        return msg

    # Cria um pacote WRQ (Write Request) em formato ProtoBuffer a partir do definido em tftp2.proto
        # para enviar um arquivo ao servidor TFTP2.
    @staticmethod
    def criar_wrq(filename):
        msg = Mensagem()# type: ignore
        msg.wrq.fname = filename
        msg.wrq.mode = 2 # Define o modo de transferência (2 = octet, conforme definido no .proto)
        return msg

    # Cria um pacote DATA, contendo dados de um bloco do arquivo.
    @staticmethod
    def criar_data(block_n, data_bytes):
        msg = Mensagem()# type: ignore
        msg.data.block_n = block_n  # Número do bloco enviado
        msg.data.message = data_bytes   # Conteúdo (bytes) desse bloco
        return msg

    # Cria um pacote ACK, que confirma o recebimento de um determinado bloco.
    @staticmethod
    def criar_ack(block_n):
        msg = Mensagem()# type: ignore
        msg.ack.block_n = block_n   # Número do bloco confirmado
        return msg

     # Cria um pacote de erro (ERROR), usado para notificar falhas durante a transferência.
    @staticmethod
    def criar_error(error_code, error_msg):
        msg = Mensagem()# type: ignore
        msg.error.errorcode = error_code    # Código do erro (enum definido no .proto)
        msg.error.errormsg = error_msg  # Mensagem de texto explicando o erro
        return msg

    # Converte uma mensagem protobuf para bytes, para enviar pelo socket.
    @staticmethod
    def to_bytes(msg):
        return msg.SerializeToString()  # Serializa mensagem para bytes (Protobuf)

    # Converte os bytes recebidos pelo socket de volta para uma mensagem protobuf.
    @staticmethod
    def from_bytes(data):
        msg = Mensagem()# type: ignore
        msg.ParseFromString(data)   # Faz parsing dos bytes recebidos e popula campos da mensagem
        return msg

    # Descobre qual é o tipo do pacote recebido (RRQ, WRQ, DATA, ACK ou ERROR) conforme definido no arquivo tftp2.proto.
    @staticmethod
    def tipo(msg):
        if msg.HasField('rrq'):
            return 'RRQ'
        elif msg.HasField('wrq'):
            return 'WRQ'
        elif msg.HasField('data'):
            return 'DATA'
        elif msg.HasField('ack'):
            return 'ACK'
        elif msg.HasField('error'):
            return 'ERROR'
        else:
            return 'UNKNOWN'