import socket
import struct
import threading
import random
import json
from time import sleep
from abc import ABC, abstractmethod
from scripts.logger import get_logger_info


class NetworkHandler(ABC):
    
    def __init__(self, IP):
        self.players : dict[str, socket.socket] = {}

        #----------------------CONST----------------------#
        self.IP = IP
        self.HEADER = 10
        self.PORT = 5050
        self.ADDR = (self.IP, self.PORT)
        self.FORMAT = "utf-8"
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        #--------------------END OF CONST----------------#

        self.socket : socket.socket = None

    def receive_msg(self, conn : socket.socket):
        # First receive the size
        size_data = conn.recv(4)  # Receive 4-byte integer
        size = struct.unpack("!I", size_data)[0]

        # Receive data in chunks
        received_data = b""

        while len(received_data) < size:
            chunk = conn.recv(min(self.HEADER, size - len(received_data)))  # Receive up to 4 bytes at a time
            if not chunk:
                break
            received_data += chunk

        return received_data.decode(self.FORMAT)

    def send_msg(self, msg : str, conn : socket.socket):
        msg = msg.encode(self.FORMAT)
        size = len(msg)

        # Send size (fixed 4-byte integer)
        conn.sendall(struct.pack("!I", size))

        # Send actual data in chunks
        for i in range(0, size, self.HEADER):
            conn.sendall(msg[i:i+self.HEADER])
            
    

            


    # def __send_msg_size__(self, msg):

    #     msg_length = len(msg)
    #     send_length = str(msg_length).encode(self.FORMAT)
    #     send_length += b' ' * (self.HEADER - len(send_length))
    #     return send_length 
    
    # def __receive_msg_size__(self, conn : socket.socket):
        
    #     while True:
    #         msg_length = self.__await__(conn, self.HEADER)
    #         try:
    #             msg_length = int(msg_length)
    #             break
    #         except:
    #             get_logger_info('CORE', str(self), True)
    #             continue

    #     return msg_length
    
    # def send_msg(self, conn : socket.socket, msg : str ):
    #     conn.send(self.__send_msg_size__(msg))
    #     conn.send(msg.encode(self.FORMAT))
            
    # def __await__(self, conn : socket.socket, header_size):

    #     while True:
    #         try:
    #             msg = conn.recv(header_size).decode(self.FORMAT)
    #             if msg:
    #                 return msg
    #         except socket.timeout as e:
    #             err = e.args[0]

    #             if err == 'timed out':
    #                 get_logger_info('CORE', str(self), True)
    #                 continue
    
    # def __await_reply__(self, conn : socket.socket, msg : str, debug : bool = False, s_type = 'CORE'):

    #     while True:
    #         try:

    #             self.send_msg(conn, msg)

    #             if debug:
    #                 print(msg)

    #             reply = self.receive_msg(conn)

    #             if reply:
    #                 return reply
                
    #         except socket.timeout as e:
    #             err = e.args[0]

    #             if err == 'timed out':
    #                 get_logger_info(s_type, msg, True)
    #                 continue
    
    # def receive_msg(self, conn : socket.socket):
    #     msg_length = self.__receive_msg_size__(conn)
    #     return self.__await__(conn, msg_length)
        
class Stopper:

    def __init__(self):
        self.stop = False

class Server(NetworkHandler):

    def __init__(self, IP):
        super().__init__(IP)
        self.__start_server__(0.1)
        
    def __start_server__(self, timeout):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.ADDR)
        # self.socket.settimeout(timeout)

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
        self.__connect__(0.1)

    # def __make_send_thread__(self, conn : socket.socket, msg, stopper : Stopper):

    #     thread = threading.Thread(target=self.send_msg, args=(conn, msg, stopper,))
    #     thread.start()

    def __connect__(self, timeout):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.ADDR)
        # self.socket.settimeout(timeout)


    

    