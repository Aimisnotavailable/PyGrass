import socket
import threading
import json
from network_handler import Server


print("[STARTING] server is starting")
Server("192.168.0.176").start()