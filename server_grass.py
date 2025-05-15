import pygame
import sys
import random
import math
import threading
from grass import Grass, GrassTile, Wind, GRASS_WIDTH
from gamehandler import GameClient, GameServer, game_grass
from scripts.logger import get_logger_info
from scripts.engine import Engine
from scripts.camera import Follow
from scripts.assets import Assets

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

    def __init__(self):
        super().__init__()

        pygame.mouse.set_visible(False)
        pygame.display.set_caption("SERVER")
        self.display_2 = pygame.Surface((300, 200))
        self.insert = False
        self.delete = False
        self.world_pos = [0, 0]
        
        self.players = {"SERVER" : {"POSITION" : self.world_pos}}
        self.id = ""

        SERVER = GameServer("192.168.0.191", game=self)

        thread = threading.Thread(target=SERVER.start)
        thread.start()

        self.force = 0

        self.camera = Follow('Follow', 0.03)

        self.mouse_offset = [0, 0]

        self.mouse_surf = pygame.Surface((RADIUS * 2, RADIUS * 2))
        self.flip = 1

        self.wind = Wind(x_pos=self.display.get_width(), speed=300)
        self.player_id = "SERVER"

    def run(self):
        global game_grass 

        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.fill((1, 50, 32))

            dt = (self.clock.tick() / 1000.0) + 1e-5

            mpos = pygame.mouse.get_pos()
            mpos = [mpos[0] // 2, mpos[1] // 2]

            self.world_pos = [int(mpos[0] + self.mouse_offset[0]), int(mpos[1] + self.mouse_offset[1])]
            
            self.players['SERVER'] = self.world_pos

            # if mpos[0] >= self.display.get_width() - 5:
            #     self.mouse_offset[0] += 100 * dt
            # elif mpos[0] <= 5:
            #     self.mouse_offset[0] -= 100 * dt

            # if mpos[1] >= self.display.get_height() - 5:
            #     self.mouse_offset[1] += 300 * dt
            # elif mpos[1] <= 5:
            #     self.mouse_offset[1] -= 300 * dt

            render_scroll = (0, 0)
            # render_scroll = self.camera.scroll(self.display, dt, (mpos[0] + self.mouse_offset[0], mpos[1] + self.mouse_offset[1]))
            m_rect = self.mouse_surf.get_rect(center=[mpos[0] + render_scroll[0], mpos[1] + render_scroll[1]])

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
            world_boundary_x = [render_scroll[0] // GRASS_WIDTH - 2, (render_scroll[0] + self.display.get_width()) // GRASS_WIDTH + 2]
            world_boundary_y = [render_scroll[1] // GRASS_WIDTH - 2, (render_scroll[1] + self.display.get_height()) // GRASS_WIDTH + 2]

            if self.insert:
                with lock:
                    for x in range(0, int(RADIUS * 2)):
                        for y in range(0, int(RADIUS * 2)):
                            pos = (m_rect[0] + x, m_rect[1] + y)
                            g_pos = f"{pos[0]//GRASS_WIDTH} ; {pos[1]//GRASS_WIDTH}"
                            if g_pos not in game_grass:
                                game_grass[g_pos] = GrassTile(((pos[0]//GRASS_WIDTH) * GRASS_WIDTH, (pos[1]//GRASS_WIDTH) * GRASS_WIDTH))

            self.wind.update(dt, render_scroll)
            # self.wind.render(self.display, render_scroll)

            p_rects = []
            p_ids = []

            for player_id, player in self.players.copy().items():
                if player:
                    # print("PLAYER DATA : ", player, "PLAYER_ID", player_id)
                    get_logger_info("CORE", f'{player}')
                    p_rect = self.mouse_surf.get_rect(center=player)
                    p_rects.append(p_rect)
                    p_ids.append(player_id)
                    
            with lock:
                for x in range(world_boundary_x[0], world_boundary_x[1]):
                    for y in range(world_boundary_y[0], world_boundary_y[1]):
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
                            grass_tile.render(self.display, render_scroll=render_scroll)
                            
            self.display.blit(self.font.render(f"{self.world_pos}", True, (0, 0, 0)), (0, 0))
            self.display.blit(self.font.render(f"FPS: {1//dt}", True, (0, 0, 0)), (200, 0))

            if self.force > 0:
                self.force = max(0, self.force - (self.force * dt))
            elif self.force < 0:
                self.force = min(0, self.force - (self.force * dt))
            
            for player_id, p_rect in zip(p_ids, p_rects):
                pygame.draw.circle(self.display, (255, 255, 255), (p_rect.center[0] - self.mouse_offset[0], p_rect.center[1] - self.mouse_offset[1]) , RADIUS, 1)
                id_surf = self.font.render(player_id, True, (0, 0, 0) if self.player_id != player_id else (255, 255, 255))
                id_rect = id_surf.get_rect(center=(p_rect.centerx, p_rect.bottom))
                self.display.blit(id_surf, id_rect)

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 0), unsetcolor=(0, 0, 0, 0))

            for offset in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
                self.display_2.blit(display_sillhouette, offset)
            
            self.display_2.blit(self.display, (0, 0))
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), (0, 0))

            pygame.display.update()
            
            # self.clock.tick(60)

Window().run()