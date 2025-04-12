import socket
import threading
import random
import json
from abc import ABC, abstractmethod

class NetworkHandler(ABC):
    
    def __init__(self, IP):
        self.players : dict[str, socket.socket] = {}

        #----------------------CONST----------------------#
        self.IP = IP
        self.HEADER = 64
        self.PORT = 5050
        self.ADDR = (self.IP, self.PORT)
        self.FORMAT = "utf-8"
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        #--------------------END OF CONST----------------#

class Server(NetworkHandler):

    def __init__(self, IP):
        super().__init__(IP)
        self.clients : dict[str : str] = {}

        self.__start_server__()

    def __start_server__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)

    def add_conn(self):
        pass
    
    def handle_client(self, conn : socket.socket, addr : str):

        print(f"[NEW CONNECTION] {addr} connected.")

        connected = True
        while connected:

            msg_length = conn.recv(self.HEADER).decode(self.FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(self.FORMAT)

                if msg == self.DISCONNECT_MESSAGE:
                    connected = False
                    break
                
                print(f"[{addr}] {msg}")
                conn.send(str(json.dumps(self.clients)).encode(self.FORMAT))
        conn.close()
    
    def __generate_id__(self):
        return "".join([chr(random.randint(65, 122)) for i in range(30)])
    
    def start(self):
        self.server.listen()
        print(f"[LISTENING] Server is listening on {self.IP}")

        while True:
            conn, addr = self.server.accept()
            self.clients[self.__generate_id__()] = ""

            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()

            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

class Client(NetworkHandler):
    def __init__(self, IP):
        super().__init__(IP)
        self.__connect__()

    def __connect__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)

    def send(self, msg : str):
        print(msg)
        message = msg.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        
        send_length += b' ' * (self.HEADER - len(send_length))
        self.client.send(send_length)
        self.client.send(message)


    

    