from network_handler import Server
import threading
import socket

from scripts.logger import get_logger_info


class TestServer(Server):
    def __init__(self, IP):
        super().__init__(IP)
    
    def start(self):
        self.socket.listen()
        
        print(f"[LISTENING] Server is listening on {self.IP}")

        client_count = -1
        while True:
            try:
                conn, addr = self.socket.accept()
            
                client_count += 1

                client_id = self.__generate_id__(client_count)
                # self.game.players[client_id] = ""

                thread = threading.Thread(target=self.handle_client, args=(conn, addr, client_id))
                thread.start()

                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")
            except socket.timeout as e:
                err = e.args[0]

                if err == 'timed out':
                    get_logger_info('CORE', ("TIMED OUT"))
                    continue

    def handle_client(self, conn, addr, client_id=""):
        print(f"[NEW CONNECTION] {addr} connected.")
        connected = True

        while connected:

            get_logger_info('CORE', ("RECEIVING MESSAGE"))
            get_logger_info('APP', self.receive_msg(conn))

        conn.close()

TestServer('192.168.0.184').start()