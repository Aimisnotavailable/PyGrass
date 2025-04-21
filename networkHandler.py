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
        self.HEADER = 4096
        self.PORT = 5050
        self.ADDR = (self.IP, self.PORT)
        self.FORMAT = "utf-8"
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        #--------------------END OF CONST----------------#

    def __send_msg_size__(self, msg):

        msg_length = len(msg)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        return send_length 
    
    def __receive_msg_size__(self, conn : socket.socket):
        
        msg_length = conn.recv(self.HEADER).decode(self.FORMAT)

        if msg_length != "":
            msg_length = int(msg_length)
            return msg_length
    
    def send_msg(self, conn : socket.socket, msg : str):

        conn.send(self.__send_msg_size__(msg))
        conn.send(msg.encode(self.FORMAT))
    
    def receive_msg(self, conn : socket.socket):

        msg_length = self.__receive_msg_size__(conn)
        return conn.recv(msg_length).decode(self.FORMAT)

class Server(NetworkHandler):

    def __init__(self, IP):
        super().__init__(IP)
        self.__start_server__()

    def __start_server__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)

    def __generate_id__(self, client_count):
        return "PLAYER " + str(client_count)
    
        return "".join([chr(random.randint(65, 122)) for i in range(30)])
    
    def handle_client(self, conn : socket.socket, addr : str, client_id = ""):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError
        

class Client(NetworkHandler):
    def __init__(self, IP):
        super().__init__(IP)
        self.__connect__()

    def __connect__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)


    

    