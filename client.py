import socket
from networkHandler import Client
from obj import TestOBJ

DISCONNECT_MESSAGE = "!DISCONNECT"
client = Client("169.254.177.202")

while True:
    if input() != 'a':
        client.send_msg(client.client, TestOBJ(socket.gethostbyname(socket.gethostname()), "HELLO WORLD").serialize())
        msg = client.receive_msg(client.client)
        if msg:
            print(msg)
    else:
        client.send(DISCONNECT_MESSAGE)
        break