import threading
from networkHandler import Client, Server


class GameClient(Client):

    def __init__(self, IP):
        super().__init__(IP)

    def send(self, game):
        while True:
            msg = f'{game.world_pos}'
            super().send(msg)

class GameServer(Server):

    def __init__(self, IP):
        super().__init__(IP)
        self.clients = []

    def handle_client(self, conn, addr):

        super().handle_client(conn, addr)