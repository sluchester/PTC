# Steps to do - Lab

https://moodle.ifsc.edu.br/mod/page/view.php?id=257637

1- ler link do moodle
2- lembrar como se usa docker
2.1- executar uma imagem docker para simular o protocolo TFTP
3- ler novamente o moodle e verificar o que é pedido para desenvolver a biblioteca inicialmente

------------------------------------------------------------------------------------------------

# Steps to do - Protocolo TFTP
- Criar um cliente TFTP. Uma biblioteca (API) que possa se comunicar com este servidor e ser reutilizada
- Fazer esqueleto de como a API será estruturada

# Comunicação Síncrona e Assíncrona
- Síncrona: só começa uma outra tarefa ao término da primeira.
- Assíncrona: 
- Python possui biblioteca: asyncio

# Endianness

## Big Endian
MSB    LSB

Addr  Addr+1
## Littlle Endian
LSB    MSB

Addr  Addr+1

# How to compile proto
```proto
    protoc --python_out=. tftp.proto
```

## Steps to Do TFTP2

Pegar o protocolo desenvolvido no primeiro projeto e acomodá-lo às regras do tftp2.proto deste repositório.

Verificar o áudio pra qualquer explicação que falte.