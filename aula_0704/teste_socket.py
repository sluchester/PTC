from socket import *

sd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)

# está entre parênteses porque é uma tupla
sd.bind(('0.0.0.0', 7000))

sd.sendto(b'123456890', ('127.0.0.1'))

print(sd)