import threading
import json
import random
from grass import Grass, GRASS_WIDTH
from networkHandler import Client, Server
# from main import Window


class GameClient(Client):

    def __init__(self, IP):
        super().__init__(IP)

    def request_world_data(self, game):
        while True:

            msg = "REQUEST_POSITION_DATA"
            self.send_msg(self.client, msg)

            msg = f'{game.world_pos}'
            self.send_msg(self.client, msg)

            game.players = self.deserialize_data()

            msg  = "REQUEST_GRASS_DATA"
            self.send_msg(self.client, msg)

            msg = game.grass_update
            self.send_msg(self.client, json.dumps(msg))

            self.convert_to_game_object(game, self.deserialize_data())
            
    def convert_to_game_object(self, game, data : dict):

        for key, val in data.items():
            game.grass[key] = Grass(val['GRASS_POS'])
        
    def deserialize_data(self):
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

                if msg == "REQUEST_POSITION_DATA":
                    
                    msg = self.receive_msg(conn)
                    self.game.players[client_id] = json.loads(msg)

                    players = self.game.players.copy()

                    reply = json.dumps(players)
                    self.send_msg(conn, reply)
                
                if msg == "REQUEST_GRASS_DATA":

                    msg = json.loads(self.receive_msg(conn))

                    if msg['GRASS_ACTION'] == 'ADD':
                        if msg['GRASS_POS'] not in self.game.grass:
                            self.game.grass[msg['GRASS_POS']] = Grass(msg['GRASS_POS_INT'], (0, random.randint(40, 255), 0), True if random.randint(0, 100) < 12 else False, random.randint(10, 20))

                    grass_msg = {}

                    for x in range(msg['BOUNDARY_X'][0], msg['BOUNDARY_X'][1]):
                        for y in range(msg['BOUNDARY_Y'][0], msg['BOUNDARY_Y'][1]):
                            key = f"{x} ; {y}"

                            if key in self.game.grass:
                                grass_msg[key] = {"GRASS_POS" : self.game.grass[key].pos}
                    
                    with open('test.json', 'w+') as fp:
                        json.dump(grass_msg, fp, indent=2)

                    reply = json.dumps(grass_msg)
                    self.send_msg(conn, reply)


        conn.close()

    # def handle_client(self, conn, addr):
    #     super().handle_client(conn, addr)