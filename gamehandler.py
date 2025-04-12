import threading
import json
from networkHandler import Client, Server
# from main import Window


class GameClient(Client):

    def __init__(self, IP):
        super().__init__(IP)

    def send(self, game):
        while True:
            msg = f'{game.world_pos}'
            self.send_msg(self.client, msg)
            game.players = json.loads(self.receive_msg(self.client))
            
class GameServer(Server):

    def __init__(self, IP):
        super().__init__(IP)
    
    # def handle_client(self, conn, addr):
    #     super().handle_client(conn, addr)