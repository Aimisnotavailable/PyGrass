import threading
import json
import random
import socket
from time import sleep
from grass import Grass, GrassTile, GRASS_WIDTH
from networkHandler import Client, Server, Stopper
# from main import Window

lock = threading.Lock()
game_grass : dict[str, GrassTile] = {}
grass_to_render : dict[str, GrassTile] = {}
req_msg : dict[str, dict] = {}

class GameClient(Client):

    def __init__(self, IP):
        super().__init__(IP)

    def __start_request__(self):
        self.wait = True

    def __await_okay_response__(self):
        return self.receive_msg(self.client) == "OKAY"
    
    def request_world_data(self, game):

        while True:
            self.request_player_position_data(game)
            self.request_grass_position_data(game)
            self.request_wind_position_data(game)
        
    def request_played_id(self):
        
        msg = "REQUEST_PLAYER_ID"
        msg = self.__await_reply__(self.socket, msg)
        
        return msg

    def request_player_position_data(self, game):
        msg = "REQUEST_POSITION_DATA" 
        self.__await_reply__(self.socket, msg)

        msg = f'{game.world_pos}'
        reply = self.__await_reply__(self.socket, msg)

        game.players = self.__deserialize_data__(reply)

        self.send_msg(self.socket, "DONE")

    def request_grass_position_data(self, game):
        global req_msg
        global grass_to_render
        with lock:
            msg  = "REQUEST_GRASS_DATA"
            rp = self.__await_reply__(self.socket, msg)

            reply = self.__await_reply__(self.socket, json.dumps(req_msg))
            self.send_msg(self.socket, "DONE")
            
            grass_to_render.update(self.__deserialize_data__(reply))


    def request_wind_position_data(self, game):

        msg = "REQUEST_WIND_DATA"
        reply = self.__await_reply__(self.socket, msg)
        reply = self.__deserialize_data__(reply)

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
        self.socket.listen()
        
        print(f"[LISTENING] Server is listening on {self.IP}")

        client_count = -1
        while True:
            try:
                conn, addr = self.socket.accept()
            
                client_count += 1

                client_id = self.__generate_id__(client_count)
                self.game.players[client_id] = ""

                thread = threading.Thread(target=self.handle_client, args=(conn, addr, client_id))
                thread.start()

                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")
            except socket.timeout as e:
                err = e.args[0]

                if err == 'timed out':
                    print("TIMED OUT")
                    continue

    def __send_okay_response__(self, conn):
        self.send_msg(conn, "OKAY")

    def handle_client(self, conn, addr, client_id=""):
        print(f"[NEW CONNECTION] {addr} connected.")
        connected = True

        while connected:
            
            msg = self.receive_msg(conn)

            if msg:
                stopper = Stopper()

                if msg == self.DISCONNECT_MESSAGE:
                    connected = False
                    break

                if msg == "REQUEST_POSITION_DATA":
                    msg = self.__await_reply__(conn, "RECEIVED")

                    # self.send_msg(self.socket, "HEHE", None)
                    
                    self.game.players[client_id] = json.loads(msg)

                    players = self.game.players.copy()

                    reply = json.dumps(players)

                    self.__await_reply__(conn, reply, debug=True)
                
                if msg == "REQUEST_GRASS_DATA":
                    msg = self.__await_reply__(conn, "RECEIVED")
                    
                    msg = json.loads(msg)
                    grass_msg = {}
                    if msg:
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
                    self.__await_reply__(conn, reply)

                if msg == "REQUEST_WIND_DATA":

                    reply = json.dumps({"WIND_POS" : self.game.wind.x_pos, "WIND_DIRECTION" : self.game.wind.dir, "WIND_SPEED" : self.game.wind.speed})
                    self.send_msg(conn, reply)
                
                if msg == "REQUEST_PLAYER_ID":
                    self.send_msg(conn, client_id)

        conn.close()

    # def handle_client(self, conn, addr):
    #     super().handle_client(conn, addr)