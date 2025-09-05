#!/usr/bin/python3
 
import sys,time
import ex1_pb2
 
msg = ex1_pb2.Ativo()
msg.nome = 'PETR4'
msg.id = 12345
msg.valor = 195
msg.timestamp = int(time.time())
 
data = msg.SerializeToString()
 
print('Mensagem codificada:', data)
 
copia = ex1_pb2.Ativo()
copia.ParseFromString(data)
 
print('Mensagem decodificada:')
print('Nome:', copia.nome)
print('Id:', copia.id)
print('Valor:', copia.valor)
print('Timestamp:', copia.timestamp)