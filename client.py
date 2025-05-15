import socket
from network_handler import Client
from obj import TestOBJ

DISCONNECT_MESSAGE = "!DISCONNECT"
client = Client("192.168.0.176")

while True:
    client.send_msg(client.client, TestOBJ(socket.gethostbyname(socket.gethostname()), "HELLO WORLD").serialize())
    print("GAGO")
    # msg = client.receive_msg(client.client)
    # if msg:
    #     print(msg)
    # else:
    #     client.send(DISCONNECT_MESSAGE)
    #     break