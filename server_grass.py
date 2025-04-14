import pygame
import sys
import random
import math
import threading
from grass import Grass, Wind, GRASS_WIDTH
from gamehandler import GameClient, GameServer, game_grass
from scripts.engine import Engine
from scripts.camera import Follow

RADIUS = 5

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

        self.display_2 = pygame.Surface((300, 200))
        self.insert = False
        self.delete = False
        self.world_pos = [0, 0]
        
        self.players = {"SERVER" : self.world_pos}
        self.id = ""

        SERVER = GameServer("192.168.0.176", game=self)

        thread = threading.Thread(target=SERVER.start)
        thread.start()

        self.force = 0

        self.camera = Follow('Follow', 0.03)

        self.mouse_offset = [0, 0]

        self.mouse_surf = pygame.Surface((RADIUS * 2, RADIUS * 2))
        self.flip = 1

        self.wind = Wind(x_pos=self.display.get_width(), speed=100)

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

            render_scroll = self.camera.scroll(self.display, dt, (mpos[0] + self.mouse_offset[0], mpos[1] + self.mouse_offset[1]))
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
            world_boundary_x = [render_scroll[0] // GRASS_WIDTH - GRASS_WIDTH, (render_scroll[0] + self.display.get_width()) // GRASS_WIDTH + GRASS_WIDTH]
            world_boundary_y = [render_scroll[1] // GRASS_WIDTH - GRASS_WIDTH, (render_scroll[1] + self.display.get_height()) // GRASS_WIDTH + GRASS_WIDTH]

            if self.insert:
                with lock:
                    for x in range(0, int(RADIUS * 2)):
                        for y in range(0, int(RADIUS * 2)):
                            pos = (m_rect[0] + x, m_rect[1] + y)
                            g_pos = f"{pos[0]//GRASS_WIDTH} ; {pos[1]//GRASS_WIDTH}"
                            if g_pos not in game_grass:
                                    game_grass[g_pos] = Grass(((pos[0]//GRASS_WIDTH) * GRASS_WIDTH, (pos[1]//GRASS_WIDTH) * GRASS_WIDTH), (0, random.randint(40, 255), 0), flower=True if random.randint(0, 100) < 12 else False, height=random.randint(10, 20)) 

            self.wind.update(dt, render_scroll)
            self.wind.render(self.display, render_scroll)

            with lock:
                for x in range(world_boundary_x[0], world_boundary_x[1]):
                    for y in range(world_boundary_y[0], world_boundary_y[1]):
                        g_pos = f"{x} ; {y}"
                        
                        if g_pos in game_grass:
                            grass : Grass = game_grass[g_pos]
                            grass_rect = grass.rect()
                            wind_force = 0

                            if self.wind.dir == "left":
                                if x > (self.wind.x_pos) // GRASS_WIDTH:
                                    wind_force = self.wind.speed
                            elif self.wind.dir == "right":
                                if x < (self.wind.x_pos + self.wind.length * GRASS_WIDTH) // GRASS_WIDTH:
                                    wind_force = -self.wind.speed
                            
                            if m_rect.colliderect(grass_rect):
                                if (m_rect[0] + m_rect[2] // 2) <= grass_rect[0]:
                                    dir = 'right'
                                else:
                                    dir = 'left'
                                grass.set_touch_rot(dir, dt)
                                grass.set_render_img()
                            else:
                                grass.update(dt, wind_force)

                            grass.render((0, 255, 0), self.display, render_scroll)
            self.display.blit(self.font.render(f"{self.world_pos}", True, (0, 0, 0)), (0, 0))

            if self.force > 0:
                self.force = max(0, self.force - (self.force * dt))
            elif self.force < 0:
                self.force = min(0, self.force - (self.force * dt))
            
            for player in self.players.values():
                if player:
                    p_rect = self.mouse_surf.get_rect(center=player)
                    pygame.draw.circle(self.display, (255, 255, 255), (p_rect.center[0] - self.mouse_offset[0], p_rect.center[1] - self.mouse_offset[1]) , RADIUS, 1)

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 0), unsetcolor=(0, 0, 0, 0))

            for offset in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
                self.display_2.blit(display_sillhouette, offset)
            
            self.display_2.blit(self.display)
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), (0, 0))

            pygame.display.update()
            # self.clock.tick(60)

Window().run()