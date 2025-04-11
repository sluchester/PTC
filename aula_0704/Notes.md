# Sockets

sd = socket (AF_INET, SOCK_DGRAM, IPPROTO_UDP)

AF_INET = família de protocolos
SOCK_DGRAM = tipo de comunicação
IPPROTO_UDP = tipo de protocolo

retorna um descritor do socket. Um ID que identifica o socket para o SO.

bind = vincular

bind(sd, sockaddr_in(*addr))
sendto()
recv