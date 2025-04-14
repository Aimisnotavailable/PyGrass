import threading
import json
import random
from grass import Grass, GRASS_WIDTH
from networkHandler import Client, Server
# from main import Window

lock = threading.Lock()
game_grass = {}

class GameClient(Client):

    def __init__(self, IP):
        super().__init__(IP)

    def request_world_data(self, game):
        self.request_player_position_data(game)
        self.request_grass_position_data(game)

    def request_player_position_data(self, game):
        msg = "REQUEST_POSITION_DATA"
        self.send_msg(self.client, msg)

        msg = f'{game.world_pos}'
        self.send_msg(self.client, msg)

        game.players = self.deserialize_data(self.receive_msg(self.client))

    def request_grass_position_data(self, game: str):

        msg  = "REQUEST_GRASS_DATA"
        self.send_msg(self.client, msg)

        self.send_msg(self.client, json.dumps(game.grass_update_msg))
        print(len(self.deserialize_data(self.receive_msg(self.client))))
    
    def deserialize_data(self, reply):
        return json.loads(reply)

class GameServer(Server):

    def __init__(self, IP, game):
        super().__init__(IP)
        self.game = game
    
    def start(self):
        self.server.listen()
        
        (f"[LISTENING] Server is listening on {self.IP}")

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

                if msg == "REQUEST_POSITION_DATA":
                    
                    msg = self.receive_msg(conn)
                    self.game.players[client_id] = json.loads(msg)

                    players = self.game.players.copy()

                    reply = json.dumps(players)
                    self.send_msg(conn, reply)
                
                if msg == "REQUEST_GRASS_DATA":
                    global game_grass
                    msg = json.loads(self.receive_msg(conn))
                    grass_msg = {}

                    with lock:
                        if msg['GRASS_ACTION'] == 'ADD':
                            if msg['GRASS_POS'] not in game_grass:
                                game_grass[msg['GRASS_POS']] = Grass(msg['GRASS_POS_INT'], (0, random.randint(40, 255), 0), True if random.randint(0, 100) < 12 else False, random.randint(10, 20))
                        else:
                            for x in range(msg['BOUNDARY_X'][0], msg['BOUNDARY_X'][1]):
                                for y in range(msg['BOUNDARY_Y'][0], msg['BOUNDARY_Y'][1]):
                                    key = f"{x} ; {y}"
                                    if key in game_grass:
                                        grass_msg[key] = {"GRASS_POS" : game_grass[key].pos, "GRASS_COLOR" : game_grass[key].color, "GRASS_POINTS" : game_grass[key].main_leaf_points, "FLOWER" : game_grass[key].flower,}
                    reply = json.dumps(grass_msg)
                    self.send_msg(conn, reply)


        conn.close()

    # def handle_client(self, conn, addr):
    #     super().handle_client(conn, addr)