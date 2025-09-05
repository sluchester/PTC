import struct

class TFTPPacket:
    'Classe base para pacotes TFTP'
    def __init__(self, opcode):
        self.opcode = opcode

    # Método para converter o pacote em bytes.
    # Cada subclasse deve implementar este método para serializar seus dados.
    # O método deve retornar uma sequência de bytes que representa o pacote TFTP.
    def to_bytes(self):
        raise NotImplementedError()

    # Método estático para criar um pacote TFTP a partir de bytes.
    # Recebe uma sequência de bytes e tenta interpretar como um pacote TFTP.
    # Dependendo do opcode, chama o construtor apropriado da subclasse.
    # Se o opcode não for reconhecido, lança uma exceção ValueError.
    @staticmethod
    def from_bytes(data):
        if len(data) < 2:
            raise ValueError("Pacote muito curto.")

        # Extrai o opcode dos primeiros 2 bytes do pacote.
        opcode = struct.unpack("!H", data[:2])[0]

        # Verifica o opcode e chama o construtor apropriado.
        # Cada subclasse deve implementar o método from_bytes para interpretar seus dados.
        # 1 é um RRQ (Read Request), 2 é um WRQ (Write Request),
        # 3 é um DATA, 4 é um ACK (Acknowledgment), 5 é um ERROR.
        if opcode == 1:
            return RRQPacket.from_bytes(data)
        elif opcode == 2:
            return WRQPacket.from_bytes(data)
        elif opcode == 3:
            return DataPacket.from_bytes(data)
        elif opcode == 4:
            return AckPacket.from_bytes(data)
        elif opcode == 5:
            return ErrorPacket.from_bytes(data)
        else:
            raise ValueError(f"Opcode desconhecido: {opcode}")

# Define os pacotes TFTP específicos, cada um com seu próprio opcode e estrutura de dados para RRQ
class RRQPacket(TFTPPacket):
    def __init__(self, filename, mode="octet"):
        super().__init__(1)
        self.filename = filename
        self.mode = mode
    # Converte o pacote RRQ em bytes.
    # O formato é: opcode (2 bytes) + nome do arquivo (string) +
    # null terminator (1 byte) + modo (string) + null terminator (1 byte).
    # Retorna uma sequência de bytes que representa o pacote RRQ.
    # O opcode é sempre 1 para RRQ.
    def to_bytes(self):
        return struct.pack("!H", self.opcode) + self.filename.encode() + b'\0' + self.mode.encode() + b'\0'

    # Método estático para criar um pacote RRQ a partir de bytes.
    # Recebe uma sequência de bytes e tenta interpretar como um pacote RRQ.
    # Divide os dados em partes usando o null terminator (b'\0').
    # O primeiro elemento é o nome do arquivo, o segundo é o modo.
    @staticmethod
    def from_bytes(data):
        parts = data[2:].split(b'\0')
        if len(parts) < 2:
            raise ValueError("Pacote RRQ malformado.")
        filename = parts[0].decode()
        mode = parts[1].decode()
        return RRQPacket(filename, mode)

# Define o pacote WRQ (Write Request) com seu próprio opcode e estrutura de dados.
# O WRQ é usado para solicitar a escrita de um arquivo no servidor TFTP.
# Ele contém o nome do arquivo e o modo de transferência (geralmente "octet").
# O opcode para WRQ é 2.
# O pacote WRQ é semelhante ao RRQ, mas é usado para solicitações de escrita.
# Ele também contém o nome do arquivo e o modo de transferência.
class WRQPacket(TFTPPacket):
    def __init__(self, filename, mode="octet"):
        super().__init__(2)
        self.filename = filename
        self.mode = mode

    # Converte o pacote WRQ em bytes.
    # O formato é: opcode (2 bytes) + nome do arquivo (string) +
    # null terminator (1 byte) + modo (string) + null terminator (1 byte).
    # Retorna uma sequência de bytes que representa o pacote WRQ.
    # O opcode é sempre 2 para WRQ.
    def to_bytes(self):
        return struct.pack("!H", self.opcode) + self.filename.encode() + b'\0' + self.mode.encode() + b'\0'

    # Método estático para criar um pacote WRQ a partir de bytes.
    # Recebe uma sequência de bytes e tenta interpretar como um pacote WRQ.
    # Divide os dados em partes usando o null terminator (b'\0').
    # O primeiro elemento é o nome do arquivo, o segundo é o modo.
    @staticmethod
    def from_bytes(data):
        parts = data[2:].split(b'\0')
        if len(parts) < 2:
            raise ValueError("Pacote WRQ malformado.")
        filename = parts[0].decode()
        mode = parts[1].decode()
        return WRQPacket(filename, mode)

# Define o pacote DATA, que é usado para enviar dados de um arquivo.
# O pacote DATA contém um número de bloco e os dados do arquivo.
# O opcode para DATA é 3.
# O número de bloco é um inteiro que indica a ordem dos dados.
# Os dados são uma sequência de bytes que representam o conteúdo do arquivo.
class DataPacket(TFTPPacket):
    def __init__(self, block_number, data):
        super().__init__(3)
        self.block_number = block_number
        self.data = data

    # Converte o pacote DATA em bytes.
    # O formato é: opcode (2 bytes) + número do bloco (2 bytes)+ dados (bytes).
    # Retorna uma sequência de bytes que representa o pacote DATA.
    # O opcode é sempre 3 para DATA.
    def to_bytes(self):
        return struct.pack("!HH", self.opcode, self.block_number) + self.data

    # Método estático para criar um pacote DATA a partir de bytes.
    # Recebe uma sequência de bytes e tenta interpretar como um pacote DATA.
    # O número do bloco é extraído dos bytes 2 a 4.
    # Os dados são o restante da sequência de bytes.
    @staticmethod
    def from_bytes(data):
        if len(data) < 4:
            raise ValueError("Pacote DATA malformado.")
        block_number = struct.unpack("!H", data[2:4])[0]
        payload = data[4:]
        return DataPacket(block_number, payload)

# Define o pacote ACK (Acknowledgment), que é usado para confirmar o recebimento de um pacote DATA.
# O pacote ACK contém o número do bloco que foi recebido.
# O opcode para ACK é 4.
# O número do bloco é um inteiro que indica qual bloco de dados foi confirmado.
# O pacote ACK é enviado pelo cliente após receber um pacote DATA do servidor.
# Ele confirma que o bloco de dados foi recebido corretamente.
# O opcode é sempre 4 para ACK.
class AckPacket(TFTPPacket):
    def __init__(self, block_number):
        super().__init__(4)
        self.block_number = block_number

    # Converte o pacote ACK em bytes.
    # O formato é: opcode (2 bytes) + número do bloco (2 bytes).
    # Retorna uma sequência de bytes que representa o pacote ACK.
    def to_bytes(self):
        return struct.pack("!HH", self.opcode, self.block_number)

    # Método estático para criar um pacote ACK a partir de bytes.
    # Recebe uma sequência de bytes e tenta interpretar como um pacote ACK.
    # O número do bloco é extraído dos bytes 2 a 4.
    @staticmethod
    def from_bytes(data):
        if len(data) < 4:
            raise ValueError("Pacote ACK malformado.")
        block_number = struct.unpack("!H", data[2:4])[0]
        return AckPacket(block_number)
# Define o pacote de erro (Error Packet), que é usado para relatar erros durante a transferência.
# O pacote de erro contém um código de erro e uma mensagem descritiva.
# O opcode para ERROR é 5.
# O código de erro é um inteiro que indica o tipo de erro.
# A mensagem de erro é uma string que descreve o erro ocorrido.
# O pacote de erro é enviado pelo servidor quando ocorre um erro durante a transferência de dados.
class ErrorPacket(TFTPPacket):
    def __init__(self, error_code, error_msg):
        super().__init__(5)
        self.error_code = error_code
        self.error_msg = error_msg

    # Converte o pacote de erro em bytes.
    # O formato é: opcode (2 bytes) + código de erro (2 bytes) + mensagem de erro (string) + null terminator (1 byte).
    # Retorna uma sequência de bytes que representa o pacote de erro.
    # O opcode é sempre 5 para ERROR.
    def to_bytes(self):
        return struct.pack("!HH", self.opcode, self.error_code) + self.error_msg.encode() + b'\0'

    # Método estático para criar um pacote de erro a partir de bytes.
    # Recebe uma sequência de bytes e tenta interpretar como um pacote de erro.
    # O código de erro é extraído dos bytes 2 a 4.
    # A mensagem de erro é o restante da sequência de bytes, até o primeiro null terminator.
    @staticmethod
    def from_bytes(data):
        if len(data) < 5:
            raise ValueError("Pacote ERROR malformado.")
        error_code = struct.unpack("!H", data[2:4])[0]
        msg = data[4:].split(b'\0')[0].decode()
        return ErrorPacket(error_code, msg)

    # Método para representar o pacote de erro como uma string.
    # Retorna uma string formatada com o código de erro e a mensagem de erro.
    def __str__(self):
        return f"ErrorPacket(code={self.error_code}, message='{self.error_msg}')"
