from Subcamada import Subcamada
from crc16.crc import CRC16

class DeteccaoErros(Subcamada):
    """
    Subcamada de detecção de erros usando CRC16 (RFC 1662).
    - Ao enviar: adiciona CRC ao quadro.
    - Ao receber: verifica CRC antes de passar para camada superior.
    """

    def __init__(self):
        super().__init__()

    def envia(self, dados: bytes):
        """
        Chamado pela camada superior.
        Calcula e adiciona CRC ao final antes de enviar.
        """
        crc = CRC16(dados)
        quadro_com_crc = crc.gen_crc()
        print(f"[DeteccaoErros] Enviando quadro com CRC: {quadro_com_crc}")

        if self.lower is not None:
            self.lower.envia(bytes(quadro_com_crc))
        else:
            print("[DeteccaoErros] Nenhuma camada inferior conectada! Quadro não enviado.")

    def recebe(self, dados: bytes):
        """
        Chamado pela camada inferior.
        Verifica CRC; se estiver correto, entrega dados sem o CRC.
        """
        if len(dados) < 2:
            print("[DeteccaoErros] Quadro muito curto para conter CRC, descartado.")
            return

        crc = CRC16(dados)
        if crc.check_crc():
            payload = dados[:-2]
            print(f"[DeteccaoErros] CRC ok, entregando payload: {payload}")

            if self.upper is not None:
                self.upper.recebe(payload)
            else:
                print("[DeteccaoErros] Nenhuma camada superior conectada!")
        else:
            print("[DeteccaoErros] Erro de CRC! Quadro descartado.")
