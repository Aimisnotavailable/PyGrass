import threading
import json
import random
from grass import Grass, GrassTile, GRASS_WIDTH
from networkHandler import Client, Server
# from main import Window

lock = threading.Lock()
game_grass : dict[str, GrassTile] = {}

class GameClient(Client):

    def __init__(self, IP):
        super().__init__(IP)

    def request_world_data(self, game):

        self.request_player_position_data(game)
        self.request_grass_position_data(game)

    def request_played_id(self):
        msg = "REQUEST_PLAYER_ID"
        self.send_msg(self.client, msg)
        
        return self.receive_msg(self.client)

    def request_player_position_data(self, game):

        msg = "REQUEST_POSITION_DATA"
        self.send_msg(self.client, msg)

        msg = f'{game.world_pos}'
        self.send_msg(self.client, msg)

        reply = self.__deserialize_data__(self.receive_msg(self.client))

        game.players = reply
        
    def request_grass_position_data(self, req_msg: str):

        msg  = "REQUEST_GRASS_DATA"
        self.send_msg(self.client, msg)

        self.send_msg(self.client, json.dumps(req_msg))
        return self.__deserialize_data__(self.receive_msg(self.client))

    def request_wind_position_data(self, game):

        msg = "REQUEST_WIND_DATA"
        self.send_msg(self.client, msg)
        reply = self.__deserialize_data__(self.receive_msg(self.client))

        game.wind.x_pos = reply['WIND_POS']
        game.wind.dir = reply['WIND_DIRECTION']
        game.wind.speed = reply['WIND_SPEED']

    def __deserialize_data__(self, reply):
        try:
            obj_data = json.loads(reply)
        except:
            with open("test.txt", "w+") as fp:
                fp.write(reply)

        return obj_data

class GameServer(Server):

    def __init__(self, IP, game):
        super().__init__(IP)
        self.game = game
    
    def start(self):
        self.server.listen()
        
        print(f"[LISTENING] Server is listening on {self.IP}")

        client_count = -1
        while True:
            conn, addr = self.server.accept()
            
            client_count += 1

            client_id = self.__generate_id__(client_count)
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
                    print("MESSAGE: ", msg)
                    self.game.players[client_id] = json.loads(msg)

                    players = self.game.players.copy()

                    reply = json.dumps(players)
                    self.send_msg(conn, reply)
                
                if msg == "REQUEST_GRASS_DATA":
                    
                    msg = json.loads(self.receive_msg(conn))
                    grass_msg = {}

                    with lock:
                        if msg['GRASS_ACTION'] == 'ADD':
                            if msg['GRASS_POS'] not in game_grass:
                                game_grass[msg['GRASS_POS']] = Grass(msg['GRASS_POS_INT'])
                        else:
                            for key in msg['KEY']:
                                if key in game_grass:
                                    grass_msg[key] = {"REPLY" : "EXIST", "GRASS_POS" : game_grass[key].pos, "GRASS_DATA" : list(game_grass[key].grass)}
                        # else:
                        #     for x in range(msg['BOUNDARY_X'][0], msg['BOUNDARY_X'][1]):
                        #         for y in range(msg['BOUNDARY_Y'][0], msg['BOUNDARY_Y'][1]):
                        #             key = f"{x} ; {y}"
                        #             if key in game_grass:
                        #                 grass_msg[key] = {"GRASS_POS" : game_grass[key].pos, "GRASS_TYPE" : game_grass[key].type}

                    reply = json.dumps(grass_msg)
                    self.send_msg(conn, reply)

                if msg == "REQUEST_WIND_DATA":

                    reply = json.dumps({"WIND_POS" : self.game.wind.x_pos, "WIND_DIRECTION" : self.game.wind.dir, "WIND_SPEED" : self.game.wind.speed})
                    self.send_msg(conn, reply)
                
                if msg == "REQUEST_PLAYER_ID":

                    self.send_msg(conn, client_id)

        conn.close()

    # def handle_client(self, conn, addr):
    #     super().handle_client(conn, addr)