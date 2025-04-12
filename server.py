import socket
import threading
import json
from networkHandler import Server


print("[STARTING] server is starting")
Server(socket.gethostbyname(socket.gethostname())).start()