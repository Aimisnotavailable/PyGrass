import pygame
import sys
import random
import math
import threading
from grass import Grass, GrassTile, Wind, GRASS_WIDTH
from gamehandler import GameClient, game_grass
from scripts.engine import Engine
from scripts.camera import Follow

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

CLIENT = GameClient("192.168.0.176")

class Window(Engine): 

    def __init__(self):
        super().__init__()

        pygame.mouse.set_visible(False)

        self.display_2 = pygame.Surface((300, 200))
        self.insert = False
        self.delete = False
        self.world_pos = [0, 0]

        pygame.display.set_caption("CLIENT")

        self.players = {}
        self.id = ""
        self.grass : dict[str:Grass] = {}
        
        self.world_boundary_x = [0, 0]
        self.world_boundary_y = [0, 0]
        
        self.grass_update_msg = {'GRASS_ACTION' : "", "BOUNDARY_X" : self.world_boundary_x, "BOUNDARY_Y" : self.world_boundary_y}

        self.force = 0

        self.camera = Follow('Follow', 0.03)

        self.mouse_offset = [0, 0]

        self.mouse_surf = pygame.Surface((RADIUS * 2, RADIUS * 2))
        self.flip = 1

        self.wind = Wind(x_pos=self.display.get_width(), speed=100)
        # CLIENT.request_wind_position_data(self)
        self.player_id = CLIENT.request_played_id()
        self.buffer = -0.1

    def __apply_force_updates__(self, grass : Grass, x_pos, y_pos, m_rect, dt, render_scroll=[0, 0]):
        grass_rect = grass.rect()
        wind_force = 0

        if self.wind.dir == "left":
            if x_pos > (self.wind.x_pos) // GRASS_WIDTH:
                wind_force = self.wind.speed
        elif self.wind.dir == "right":
            if x_pos < (self.wind.x_pos + self.wind.length * GRASS_WIDTH) // GRASS_WIDTH:
                wind_force = -self.wind.speed
        
        if m_rect.colliderect(grass_rect):
            if (m_rect[0] + m_rect[2] // 2) <= grass_rect[0]:
                dir = 'right'
            else:
                dir = 'left'
            grass.set_touch_rot(dir, dt)
        else:
            grass.update(dt, wind_force)

        grass.render((0, 255, 0), self.display, (render_scroll[0] - self.mouse_offset[0], render_scroll[1] - self.mouse_offset[1]))

    def run(self):
        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.fill((1, 50, 32))

            dt = (self.clock.tick(60) / 1000.0) + 1e-5

            mpos = pygame.mouse.get_pos()
            mpos = [mpos[0] // 2, mpos[1] // 2]

            self.world_pos = [int(mpos[0] + self.mouse_offset[0]), int(mpos[1] + self.mouse_offset[1])]

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
            self.world_boundary_x = [render_scroll[0] // GRASS_WIDTH - 2, (render_scroll[0] + self.display.get_width()) // GRASS_WIDTH + 2]
            self.world_boundary_y = [render_scroll[1] // GRASS_WIDTH - 2, (render_scroll[1] + self.display.get_height()) // GRASS_WIDTH + 2]
            self.grass_update_msg = {'GRASS_ACTION' : "", "BOUNDARY_X" : self.world_boundary_x, "BOUNDARY_Y" : self.world_boundary_y}
            
            
            # if self.insert:
            #     for x in range(0, int(RADIUS * 2)):
            #         for y in range(0, int(RADIUS * 2)):
            #             pos = (m_rect[0] + x, m_rect[1] + y)
            #             g_pos = f"{pos[0]//GRASS_WIDTH} ; {pos[1]//GRASS_WIDTH}"
            #             if g_pos not in self.grass:
            #                 self.grass[g_pos] = Grass(((pos[0]//GRASS_WIDTH) * GRASS_WIDTH, (pos[1]//GRASS_WIDTH) * GRASS_WIDTH), (0, random.randint(40, 255), 0), True if random.randint(0, 100) < 12 else False, random.randint(10, 20)) 
            
            print(CLIENT.request_played_id())
            CLIENT.request_player_position_data(self)

            self.wind.update(dt, render_scroll=render_scroll)

            
            req_msg = {"GRASS_ACTION" : "", "KEY" : []}
            p_rects = []
            p_ids = []

            for player_id, player in self.players.items():
                if player:
                    p_rect = self.mouse_surf.get_rect(center=player)
                    p_rects.append(p_rect)
                    p_ids.append(player_id)

            # print(f'X : {self.world_boundary_x} Y: {self.world_boundary_y}')
            for x in range(self.world_boundary_x[0], self.world_boundary_x[1]):
                for y in range(self.world_boundary_y[0], self.world_boundary_y[1]):
                    g_pos = f"{x} ; {y}"
                    
                    if g_pos in self.grass:
                        grass_tile : GrassTile = self.grass[g_pos]

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
                    else:
                        req_msg['KEY'].append(g_pos)

            if ((self.buffer + 0.1) % 50) == 0:
                CLIENT.request_wind_position_data(self)
                if len(req_msg['KEY']):
                    print(len(req_msg['KEY']))
                    reply = CLIENT.request_grass_position_data(req_msg=req_msg)
                    if len(reply):
                        for key, data in reply.items():
                            if data['REPLY'] == "EXIST":
                                grass_tile : GrassTile = GrassTile(data['GRASS_POS'])
                                for data in data['GRASS_DATA']:
                                    if not data in grass_tile.grass:
                                        data_list = data.split(' ; ')
                                        grass_data = {"KEY" : data, "POS" : [int(data_list[0]), int(data_list[1])], "TYPE" : int(data_list[2])}
                                        grass_tile.add_blade(grass_data=grass_data)
                                self.grass[key] = grass_tile

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

            self.display.blit(self.font.render(f"{self.world_pos}", True, (0, 0, 0)), (0, 0))
            self.display.blit(self.font.render(f"FPS: {1//dt}", True, (0, 0, 0)), (200, 0))
            for offset in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
                self.display_2.blit(display_sillhouette, offset)
            
            self.display_2.blit(self.display, (0, 0))
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), (0, 0))

            pygame.display.update()
            # self.clock.tick(60)

Window().run()