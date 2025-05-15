from networkHandler import Client
from networkHandler import Server
import random

class TestClient(Client):

    def __init__(self, IP):
        super().__init__(IP)
    
    def __generate_id__(self):
        # return "PLAYER " + str(client_count)
    
        return "".join([chr(random.randint(65, 122)) for i in range(3000)])

client = TestClient('192.168.0.184')

while True:
    
    #msg = input('Input Here: ')
    client.send_msg(client.__generate_id__() ,client.socket)