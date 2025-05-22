import pygame
import sys
import random
import math
import threading
import screeninfo
from grass import Grass, GrassTile, Wind, GRASS_WIDTH
from gamehandler import GameClient, GameServer, game_grass
from scripts.logger import get_logger_info
from scripts.engine import Engine
from scripts.camera import Follow
from scripts.assets import Assets
from scripts.player import Player

RADIUS = 20

RESISTANCE = 20

BOUNDARY_KEYS = {"left_wind" : (0, 1, 1), "right_wind" : (1, 0, -1), "default" : (0, 1, 1)}

OFFSETS = [(0, 1),
           (0, -1),
           (1, 0),
           (-1, 0),
           (1, 1),
           (-1, 1),
           (1, -1),
           (-1,-1),]

lock = threading.Lock()

class Window(Engine): 

    def __init__(self, dim):
        super().__init__(dim=dim)

        pygame.mouse.set_visible(False)
        pygame.display.set_caption("SERVER")
        self.display_2 = pygame.Surface(self.display.get_size())
        self.insert = False
        self.delete = False
        self.world_pos = [0, 0]
        
        self.player_id = "SERVER"
        player = Player(self.world_pos, self.player_id, game=self, is_self=True)

        self.players = { player.id : {"POSITION" : player.pos}}
        self.player_obj : dict[str, Player] = { player.id : player }

        self.id = ""

        SERVER = GameServer(game=self)

        thread = threading.Thread(target=SERVER.start)
        thread.start()

        self.force = 0

        self.camera = Follow('Follow', 0.03)

        self.mouse_offset = [0, 0]

        self.flip = 1

        self.wind = Wind(x_pos=self.display.get_width(), speed=300)
        

    def run(self):
        global game_grass 

        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.fill((1, 50, 32))

            dt = (self.clock.tick() / 1000.0) + 1e-5

            mpos = pygame.mouse.get_pos()
            mpos = [mpos[0] // 2, mpos[1] // 2]

            self.world_pos = [int(mpos[0] + self.mouse_offset[0]), int(mpos[1] + self.mouse_offset[1])]
            self.players[self.player_id] = self.world_pos

            if mpos[0] >= self.display.get_width() - 5:
                self.mouse_offset[0] += 100 * dt
            elif mpos[0] <= 5:
                self.mouse_offset[0] -= 100 * dt

            if mpos[1] >= self.display.get_height() - 5:
                self.mouse_offset[1] += 300 * dt
            elif mpos[1] <= 5:
                self.mouse_offset[1] -= 300 * dt

            render_scroll = (0, 0)
            # render_scroll = self.camera.scroll(self.display, dt, (mpos[0] + self.mouse_offset[0], mpos[1] + self.mouse_offset[1]))
            
            if not int(self.force):
                self.flip *= -1
                self.force = 100 * self.flip

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.insert = True
                        
                    if event.button == 3:
                        self.delete = True
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.insert = False
                    if event.button == 3:
                        self.delete = False

            # WORLD GRID POSITIONS
            world_boundary_x = [self.mouse_offset[0] // GRASS_WIDTH - 2, (self.mouse_offset[0] + self.display.get_width()) // GRASS_WIDTH + 2]
            world_boundary_y = [self.mouse_offset[1] // GRASS_WIDTH - 2, (self.mouse_offset[1] + self.display.get_height()) // GRASS_WIDTH + 2]

            if self.insert:
                with lock:
                    for x in range(0, int(RADIUS * 2)):
                        for y in range(0, int(RADIUS * 2)):
                            pos = (self.player_obj[self.player_id].rect.centerx + x, self.player_obj[self.player_id].rect.centery + y)
                            g_pos = f"{pos[0]//GRASS_WIDTH} ; {pos[1]//GRASS_WIDTH}"
                            if g_pos not in game_grass:
                                game_grass[g_pos] = GrassTile(((pos[0]//GRASS_WIDTH) * GRASS_WIDTH, (pos[1]//GRASS_WIDTH) * GRASS_WIDTH))

            self.wind.update(dt, render_scroll)
            # self.wind.render(self.display, render_scroll)

            p_rects = []
            for player_id, player_pos in self.players.copy().items():
                if player_pos:
                    # print("PLAYER DATA : ", player, "PLAYER_ID", player_id)
                    # get_logger_info("CORE", f'{player}')
                    if not player_id in self.player_obj:
                        self.player_obj[player_id] = Player(player_pos, player_id, game=self, is_self=(self.player_id == player_id))
                    
                    player = self.player_obj[player_id]

                    player.update(player_pos)
                    p_rects.append(player.rect)
            
            with lock:
                for x in range(int(world_boundary_x[0]), int(world_boundary_x[1])):
                    for y in range(int(world_boundary_y[0]), int(world_boundary_y[1])):
                        g_pos = f"{x} ; {y}"
                        
                        if g_pos in game_grass:
                            grass_tile : GrassTile = game_grass[g_pos]
                            wind_force = 0

                            if self.wind.dir == "left":
                                    if x > (self.wind.x_pos) // GRASS_WIDTH:
                                        wind_force = self.wind.speed * 0.4
                            elif self.wind.dir == "right":
                                if x < (self.wind.x_pos + self.wind.length * GRASS_WIDTH) // GRASS_WIDTH:
                                    wind_force = -self.wind.speed * 0.4

                            for grass in grass_tile.grass.values():
                                grass_rect = grass.rect()
                                for p_rect in p_rects:
                                    if p_rect.colliderect(grass_rect):
                                        if (p_rect[0] + p_rect[2] // 2) <= grass_rect[0]:
                                            dir = 'right'
                                        else:
                                            dir = 'left'
                                        grass.set_touch_rot(dir, dt)
                            
                            grass_tile.update(dt, wind_force=wind_force)
                            grass_tile.render(self.display, render_scroll=self.mouse_offset)

            for player_id in self.player_obj:
                self.player_obj[player_id].render(self.display, self.mouse_offset)

            self.display.blit(self.font.render(f"{self.world_pos}", True, (0, 0, 0)), (0, 0))
            self.display.blit(self.font.render(f"FPS: {1//dt}", True, (0, 0, 0)), (200, 0))

            if self.force > 0:
                self.force = max(0, self.force - (self.force * dt))
            elif self.force < 0:
                self.force = min(0, self.force - (self.force * dt))
            
            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 0), unsetcolor=(0, 0, 0, 0))

            for offset in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
                self.display_2.blit(display_sillhouette, offset)
            
            self.display_2.blit(self.display, (0, 0))
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), (0, 0))

            pygame.display.update()
            
            # self.clock.tick(60)

dim = (screeninfo.get_monitors()[0].width - 100, screeninfo.get_monitors()[0].height-100)
Window(dim).run()