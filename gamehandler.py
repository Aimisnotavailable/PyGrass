"""
game_handler.py

Defines game-specific networking logic for the client and server.
Message types include:
  - "RPI": Request Player ID.
  - "RPD": Request Player Data.
  - "RGD": Request Grass Data.
  - "RWD": Request Wind Data.
"""

import threading
import json
import socket
from time import sleep
from grass import Grass, GrassTile, GRASS_WIDTH
from network_handler import Client, Server, Stopper
from scripts.logger import get_logger_info

# Global variables for shared grass-related data
lock = threading.Lock()
game_grass: dict[str, GrassTile] = {}
grass_to_render: dict[str, GrassTile] = {}
req_msg: dict = {}  # Should be structured based on the client request

class GameClient(Client):
    """
    Client-side network handler for game data.
    Uses distinct message types for player, grass, and wind data.
    """
    def __init__(self, IP: str):
        super().__init__(IP)

    def request_world_data(self, game) -> None:
        """
        Continuously requests game data from the server.
        You can extend this to include player and wind updates as needed.
        """
        while True:
            # Request Grass Data (note: using message type "RGD")
            self.request_grass_position_data(game)
            # Optionally add other requests:
            self.request_player_position_data(game)
            self.request_wind_position_data(game)
            get_logger_info('APP', "World data request successful", True)
            sleep(0.05)  # Slight pause can help avoid overloading the network

    def request_played_id(self) -> str:
        """
        Requests a unique player ID from the server.
        """
        msg = json.dumps({'TYPE': "RPI", 'PAYLOAD': None})
        self.send_msg(self.socket, msg, s_type='APP')
        reply = self.receive_msg(self.socket)
        return reply

    def request_player_position_data(self, game) -> None:
        """
        Sends the current player position (world position) to the server.
        Expects the server to respond with all players' data.
        """
        payload = {'POSITION': game.world_pos}
        msg = json.dumps({'TYPE': "RPD", 'PAYLOAD': payload})

        self.send_msg(self.socket, msg, s_type='APP')
        reply = self.receive_msg(self.socket)

        game.players = self.__deserialize_data__(reply)

    def request_grass_position_data(self, game) -> None:
        """
        Requests grass tile data from the server based on the current requirement.
        Uses a separate message type "RGD" to avoid confusion with player data.
        """
        global req_msg, grass_to_render
        with lock:
            msg = json.dumps({'TYPE': "RGD", 'PAYLOAD': req_msg})
            self.send_msg(self.socket, msg, s_type='APP')
            reply = self.receive_msg(self.socket)
            new_data = self.__deserialize_data__(reply)
            # Merge new grass data into the global dictionary
            grass_to_render.update(new_data)

        get_logger_info('APP', f'Successfully grass request total size {len(new_data)}')
        
    def request_wind_position_data(self, game) -> None:
        """
        Requests the current wind parameters from the server and updates the game.
        """
        msg = json.dumps({'TYPE': "RWD", 'PAYLOAD': None})
        self.send_msg(self.socket, msg, s_type='APP')
        reply = self.receive_msg(self.socket)
        data = self.__deserialize_data__(reply)
        # Update the game's wind: assume keys exist
        game.wind.x_pos = data.get('WIND_POS', game.wind.x_pos)
        game.wind.dir = data.get('WIND_DIRECTION', game.wind.dir)
        game.wind.speed = data.get('WIND_SPEED', game.wind.speed)

    def __deserialize_data__(self, reply: str) -> dict:
        """
        Attempts to decode JSON data from the reply.
        If decoding fails, logs the raw reply for debugging.
        """
        try:
            if reply:
                return json.loads(reply)
        except Exception as e:
            with open("debug_raw_data.txt", "w+") as fp:
                fp.write(reply)
            get_logger_info('ERROR', f"Deserialization error: {e}", True)
        return {}

class GameServer(Server):
    """
    Server-side network handler for game data.
    Manages player connections, updates grass state, and sends wind data.
    """
    def __init__(self, game):
        super().__init__()
        self.game = game  # Game should hold players, wind, etc.
    
    def start(self) -> None:
        """
        Begins listening for client connections and spawns a new thread for each client.
        """
        self.socket.listen()
        get_logger_info('CORE', f"[LISTENING] Server is listening on {self.ADDR}")

        client_count = 0
        while True:
            try:
                conn, addr = self.socket.accept()
                client_id = self.__generate_id__(client_count)
                # Initialize player's data in the game state
                self.game.players[client_id] = {}
                threading.Thread(target=self.handle_client, args=(conn, addr, client_id), daemon=True).start()
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
                client_count += 1
            except socket.timeout as e:
                # If a timeout occurs, simply continue listening
                if e.args[0] == 'timed out':
                    continue

    def __send_okay_response__(self, conn: socket.socket) -> None:
        """Sends a simple acknowledgement message."""
        self.send_msg(conn, "OKAY")

    def handle_client(self, conn: socket.socket, addr: str, client_id: str = "") -> None:
        """
        Processes incoming messages from a single client.
        Routes the request based on the message type.
        """
        print(f"[NEW CONNECTION] {addr} connected as {client_id}.")
        connected = True

        while connected:
            try:
                raw_msg = self.receive_msg(conn)
            except ConnectionError:
                break  # Stop processing if connection is lost

            if raw_msg:
                try:
                    msg = json.loads(raw_msg)
                except json.JSONDecodeError:
                    continue

                msg_type = msg.get('TYPE', '')
                payload : dict[str, object] = msg.get('PAYLOAD', None)
                
                if msg_type == self.DISCONNECT_MESSAGE:
                    connected = False
                    break

                elif msg_type == "RPD":
                    # Update the player's position from the received payload.
                    self.game.players[client_id] = payload['POSITION']
                    
                    reply = json.dumps(self.game.players)
                    self.send_msg(conn, reply, s_type='RPD', debug=False)

                elif msg_type == "RGD":
                    # Process grass data requests:
                    grass_reply = {}
                    if payload:
                        with lock:
                            if payload.get('GRASS_ACTION') == 'ADD':
                                grass_pos = payload.get('GRASS_POS')
                                grass_pos_int = payload.get('GRASS_POS_INT')
                                if grass_pos and (grass_pos not in game_grass):
                                    game_grass[grass_pos] = Grass(grass_pos_int)
                            else:
                                # For every requested key, if the grass exists send back its data.
                                for key in payload.get('KEY', []):
                                    if key in game_grass:
                                        grass_tile = game_grass[key]
                                        grass_reply[key] = {
                                            "REPLY": "EXIST",
                                            "GRASS_POS": grass_tile.pos,
                                            "GRASS_DATA": list(grass_tile.grass)
                                        }
                    self.send_msg(conn, json.dumps(grass_reply))
                
                elif msg_type == "RWD":
                    wind_data = {
                        "WIND_POS": self.game.wind.x_pos,
                        "WIND_DIRECTION": self.game.wind.dir,
                        "WIND_SPEED": self.game.wind.speed
                    }
                    self.send_msg(conn, json.dumps(wind_data))
                
                elif msg_type == "RPI":
                    # When the client requests its player ID, send it back.
                    self.send_msg(conn, client_id)
        
        conn.close()
        print(f"[DISCONNECTED] {addr} disconnected.")

