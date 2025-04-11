import http.client

# instancia um cliente HTTP, que será usada para se comunicar com www.ifsc.edu.br
conn = http.client.HTTPSConnection("www.sj.ifsc.edu.br")

# Usa a primitiva "request", para enviar uma requisição do tipo GET para
# o servidor, para obter o documento "/"
conn.request("GET", "/")

# Usa a primitiva "response", para obter a resposta vinda do servidor
r1 = conn.getresponse()

# Mostra algumas informações contidas na resposta
print(r1.status, r1.reason)

# Mostra o conteúdo da mensagem de resposta, caso exista
data = r1.read()
print(data.decode())