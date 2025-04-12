import threading
from networkHandler import Client, Server


class GameClient(Client):

    def __init__(self, IP):
        super().__init__(IP)

    def send(self, game):
        while True:
            msg = f'{game.world_pos}'
            self.send_msg(self.client, msg)
            print(self.receive_msg(self.client))

class GameServer(Server):

    def __init__(self, IP):
        super().__init__(IP)
    
    def handle_client(self, conn, addr):
        super().handle_client(conn, addr)