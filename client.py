import socket
from networkHandler import Client
from obj import TestOBJ

DISCONNECT_MESSAGE = "!DISCONNECT"
client = Client("169.254.177.202")

while True:
    if input() != 'a':
        client.send(TestOBJ(socket.gethostbyname(socket.gethostname()), "HELLO WORLD").serialize())
        msg = client.client.recv(client.HEADER).decode(client.FORMAT)
        print(msg)
    else:
        client.send(DISCONNECT_MESSAGE)
        break