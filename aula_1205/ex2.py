#!/usr/bin/python3
 
import sys,time
from ex2_pb2 import Ativo, Valor

ativo = Ativo()
ativo.nome = 'CASH3'
ativo.id = 1
 
valor = Valor(valor=10, timestamp=1000)
ativo.valores.append(valor)
valor = Valor(valor=20, timestamp=2000)
ativo.valores.append(valor)
valor = Valor(valor=30, timestamp=3000)
ativo.valores.append(valor)
valor = Valor(valor=40, timestamp=4000)
ativo.valores.append(valor)

msg_encoded = ativo.SerializeToString()
 
print('Mensagem codificada:', msg_encoded)

copia = Ativo()
copia.ParseFromString(msg_encoded)
copia_valor = Valor()
copia_valor.ParseFromString(msg_encoded)

print(copia)

# print('Mensagem decodificada:')
# print('Nome:', copia.nome)
# print('Id:', copia.id)
# print('Valor:', copia_valor.valor)
# print('Timestamp:', copia_valor.timestamp)
