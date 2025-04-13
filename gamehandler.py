import threading
import json
from networkHandler import Client, Server
# from main import Window


class GameClient(Client):

    def __init__(self, IP):
        super().__init__(IP)

    def send_pos(self, game):
        while True:
            msg = f'{game.world_pos}'
            self.send_msg(self.client, msg)

            game.players = self.request_player_pos()

            # game.grass = json.loads(self.receive_msg(self.client))

            # print(game.grass)

    def request_player_pos(self):
        return json.loads(self.receive_msg(self.client))
            
class GameServer(Server):

    def __init__(self, IP, game):
        super().__init__(IP)
        self.game = game
    
    def start(self):
        self.server.listen()
        print(f"[LISTENING] Server is listening on {self.IP}")

        while True:
            conn, addr = self.server.accept()
            
            client_id = self.__generate_id__()
            self.game.players[client_id] = ""

            thread = threading.Thread(target=self.handle_client, args=(conn, addr, client_id))
            thread.start()

            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")

    def handle_client(self, conn, addr, client_id=""):
        print(f"[NEW CONNECTION] {addr} connected.")
        connected = True

        while connected:

            msg = self.receive_msg(conn)
            
            if msg:
                if msg == self.DISCONNECT_MESSAGE:
                    connected = False
                    break

                self.game.players[client_id] = json.loads(msg)

                players = self.game.players.copy()

                reply = json.dumps(players)
                self.send_msg(conn, reply)

        conn.close()

    # def handle_client(self, conn, addr):
    #     super().handle_client(conn, addr)