"""
network_handler.py

Defines the low-level networking functionality for both Server and Client.
Handles sending and receiving JSON‐based messages where each message is prefixed
with a 4‐byte size header.
"""

import socket
import struct
import threading
import random
import json
from scripts.logger import get_logger_info
from abc import ABC, abstractmethod

class NetworkHandler(ABC):
    """
    Abstract base class for network handlers.
    """
    def __init__(self, IP: str = '', port=5050):
        self.IP: str = IP
        self.PORT: int = port
        self.ADDR = (self.IP, self.PORT)
        self.HEADER: int = 10         # Maximum chunk size for send/receive
        self.FORMAT: str = "utf-8"
        self.DISCONNECT_MESSAGE: str = "!DISCONNECT"
        # For keeping track of connected sockets (if needed)
        self.players: dict[str, socket.socket] = {}
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _recv_all(self, conn: socket.socket, length: int) -> bytes:
        """Receive exactly 'length' bytes from the socket."""
        data = b""
        while len(data) < length:
            more = conn.recv(length - len(data))
            if not more:
                raise ConnectionError("Socket connection closed unexpectedly.")
            data += more
        return data

    def receive_msg(self, conn: socket.socket) -> str:
        """
        First receives a 4-byte integer indicating the size of the upcoming
        message, then receives the full message.
        """
        size_data = self._recv_all(conn, 4)
        size = struct.unpack("!I", size_data)[0]
        message_bytes = self._recv_all(conn, size)
        return message_bytes.decode(self.FORMAT)

    def send_msg(self, conn: socket.socket, msg: str, s_type: str = '', debug: bool = False) -> None:
        """
        Encodes and sends the message with a 4-byte size prefix.
        """
        encoded_msg = msg.encode(self.FORMAT)
        size = len(encoded_msg)
        # Send the message size as a 4-byte integer
        conn.sendall(struct.pack("!I", size))
        # Now send the message data in chunks
        for i in range(0, size, self.HEADER):
            conn.sendall(encoded_msg[i:i+self.HEADER])
        if debug:
            get_logger_info('CORE', f"[{s_type}] Sent message: {msg}")
    
    def __get_local_ip__(self) -> str:
        """ Retrieves the local IP address by establishing a temporary connection. """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))  # Google's public DNS server (doesn't actually send data)
                return s.getsockname()[0]
        except socket.error:
            return "127.0.0.1"  # Fallback to localhost

class Stopper:
    """
    A simple class that can be used to signal threads to stop
    """
    def __init__(self):
        self.stop = False

class Server(NetworkHandler):
    """
    Server class derived from NetworkHandler.
    Sets up the listening socket and provides a stub for handling clients.
    """
    def __init__(self):
        super().__init__()
        self.__start_server__()
    
    def __start_server__(self, timeout: float = 0.1):
        """Create and bind the server socket."""

        self.IP = '0.0.0.0' # self.__get_local_ip__()
        self.ADDR = (self.IP, self.PORT)
        self.socket.bind(self.ADDR)

        # Optionally set a timeout if desired:
        # self.socket.settimeout(timeout)

    def __generate_id__(self, client_count: int) -> str:
        """Generates a unique client ID."""
        return f"PLAYER {client_count}"

    @abstractmethod
    def handle_client(self, conn: socket.socket, addr: str, client_id: str = "") -> None:
        """
        To be overridden by subclasses: handles client communication.
        """
        raise NotImplementedError

    @abstractmethod
    def start(self) -> None:
        """
        To be overridden by subclasses: main loop accepting clients.
        """
        raise NotImplementedError

class Client(NetworkHandler):
    """
    Client class derived from NetworkHandler.
    Connects to the server upon initialization.
    """
    def __init__(self, IP: str, port=5050):
        super().__init__(IP, port)
        self.__connect__()
    
    def __connect__(self, timeout: float = 0.1) -> None:
        """Create and connect the client socket."""
        self.socket.connect(self.ADDR)
        # Optionally set a timeout if desired:
        # self.socket.settimeout(timeout)