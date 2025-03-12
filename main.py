import pygame
import sys
import random
import math
from scripts.engine import Engine
from scripts.camera import Follow

GRASS_WIDTH = 7
LIGHT_LEVELS = 8
MAX_ROT = 50
DIR = {'left' : -1, 'right' : 1}

RESISTANCE = 20

BOUNDARY_KEYS = {"left_wind" : (0, 1, 1), "right_wind" : (1, 0, -1), "default" : (0, 1, 1)}

class Grass:
    def __init__(self, pos=(0, 0), color=(0, 255, 0), flower = False, height=20):
        self.pos : list = list(pos)
        self.height = height

        self.direction = random.choice([1, -1])
        self.main_leaf_points = [[GRASS_WIDTH * max(0.3, random.random() - 0.5), self.height * (random.random() + 0.5)], [GRASS_WIDTH // max(1, (3 * random.random() + 0.5)) , random.random()], [GRASS_WIDTH * 0.8, self.height * (random.random() + 0.5)], [GRASS_WIDTH // max(1.4, (3 * random.random() + 0.5)), self.height]]

        self.img = pygame.Surface((GRASS_WIDTH, self.height), pygame.SRCALPHA)
        self.img_touch = pygame.Surface((GRASS_WIDTH, self.height), pygame.SRCALPHA)
        self.touch_force = 0

        self.render_img = self.img

        self.total_force = 0
        self.current_rot = 0

        self.flower = False

        if flower:
            self.flower = True
            self.flower_color = (255, 255, 0)

        self.color = color
        self.shadow_color = (self.color[0], self.color[1] - 40, self.color[2])

        self.img.fill((0, 0, 0, 0))
        pygame.draw.polygon(self.img, self.color, self.main_leaf_points)
        pygame.draw.polygon(self.img_touch, self.shadow_color, self.main_leaf_points)

        if self.flower:
            flower_points = [self.main_leaf_points[0], self.main_leaf_points[1], self.main_leaf_points[2]]
            pygame.draw.polygon(self.img, self.flower_color, flower_points)
            pygame.draw.polygon(self.img_touch, self.flower_color, flower_points)


    def set_render_img(self):
        self.render_img = self.img_touch

    def rect(self):
        return pygame.Rect(*self.pos, *self.img.get_size())
    
    def update(self, dt = 0, wind_force = 10):
        self.render_img = self.img
        
        if wind_force > 0:
            self.current_rot = min(MAX_ROT, self.current_rot + wind_force * dt)
        else:
            self.current_rot = max(-MAX_ROT, self.current_rot + wind_force * dt)

        if wind_force == 0:
            if self.current_rot > 0 :
                self.current_rot = max(0, self.current_rot - MAX_ROT * 2 * dt)
            else:
                self.current_rot = min(0, self.current_rot + MAX_ROT * 2 * dt)

    def set_touch_rot(self, dir, dt):
        if dir == "left":
            self.current_rot = self.current_rot = min(MAX_ROT, self.current_rot + MAX_ROT * 5 * dt)
        elif dir == "right":
            self.current_rot = self.current_rot = max(-MAX_ROT, self.current_rot - MAX_ROT * 5 * dt)
        
    def render(self, color, surf : pygame.Surface, render_scroll=(0, 0)):
        img = pygame.transform.rotate(self.render_img, self.current_rot)
        img_rect = img.get_rect(center=(self.pos[0] + math.cos(math.radians(self.current_rot)), self.pos[1] + math.sin(math.radians(self.current_rot))))
        surf.blit(img, (img_rect[0] - render_scroll[0], img_rect[1] - render_scroll[1]))

class Wind:

    def __init__(self, length = 10, x_pos = 0, speed = 200, dir="left"):
        self.length = length
        self.x_pos = x_pos
        self.dir = dir
        self.speed = speed
        self.max_travel = x_pos

    def update(self, dt, render_scroll = (0, 0)):
        if self.x_pos < (render_scroll[0] - self.length * 2 * GRASS_WIDTH):
            self.dir = "right"
        elif self.x_pos > (render_scroll[0] + self.max_travel + self.length * GRASS_WIDTH):
            self.dir = "left"
        self.x_pos += self.speed * dt * DIR[self.dir]

    def render(self, surf, render_scroll= (0, 0)):
        pygame.draw.rect(surf, (255, 255, 255), (self.x_pos - render_scroll[0], 0, self.length * GRASS_WIDTH, GRASS_WIDTH))
        
class Window(Engine): 

    def __init__(self):
        super().__init__()

        pygame.mouse.set_visible(False)

        self.display_2 = pygame.Surface((300, 200))
        self.insert = False
        self.delete = False

        self.grass : dict[str:Grass] = {}
        self.force = 0

        self.camera = Follow('Follow', 0.03)

        self.mouse_offset = [0, 0]

        self.mouse_surf = pygame.Surface((40, 40))
        self.flip = 1

        self.wind = Wind(x_pos=self.display.get_width(), speed=100)

    def run(self):
        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.fill((1, 50, 32))

            dt = (self.clock.tick() / 1000.0) + 1e-5

            mpos = pygame.mouse.get_pos()
            mpos = [mpos[0] // 2, mpos[1] // 2]
            
            if mpos[0] >= self.display.get_width() - 5:
                self.mouse_offset[0] += 100 * dt
            elif mpos[0] <= 5:
                self.mouse_offset[0] -= 100 * dt

            if mpos[1] >= self.display.get_height() - 5:
                self.mouse_offset[1] += 300 * dt
            elif mpos[1] <= 5:
                self.mouse_offset[1] -= 300 * dt

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
            world_size = [world_boundary_x[1] - world_boundary_x[0], world_boundary_y[1] - world_boundary_y[0]]

            if self.insert:
                pos = m_rect.center
                g_pos = f"{pos[0]//GRASS_WIDTH} ; {pos[1]//GRASS_WIDTH}"
                
                if g_pos not in self.grass:
                    self.grass[g_pos] = Grass(((pos[0]//GRASS_WIDTH) * GRASS_WIDTH, (pos[1]//GRASS_WIDTH) * GRASS_WIDTH), (0, random.randint(150, 255), 0), True if random.randint(0, 100) < 12 else False, random.randint(10, 20)) 

            self.wind.update(dt, render_scroll)
            self.wind.render(self.display, render_scroll)

            for x in range(world_boundary_x[0], world_boundary_x[1]):
                for y in range(world_boundary_y[0], world_boundary_y[1]):
                    g_pos = f"{x} ; {y}"
                    
                    if g_pos in self.grass:
                        grass : Grass = self.grass[g_pos]
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

            if self.force > 0:
                self.force = max(0, self.force - (self.force * dt))
            elif self.force < 0:
                self.force = min(0, self.force - (self.force * dt))
            
            pygame.draw.circle(self.display, (255, 255, 255), (m_rect.center[0] - render_scroll[0], m_rect.center[1] - render_scroll[1]) , 20, 1)

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 0), unsetcolor=(0, 0, 0, 0))

            for offset in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
                self.display_2.blit(display_sillhouette, offset)
            
            self.display_2.blit(self.display)
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), (0, 0))

            pygame.display.update()
            # self.clock.tick(60)

Window().run()