import threading
from networkHandler import Client, Server


class GameClient(Client):

    def __init__(self, IP):
        super().__init__(IP)
    
    def send(self, game):
        while True:
            msg = f'{game.world_pos}'
            super().send(msg)