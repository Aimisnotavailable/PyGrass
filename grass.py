import pygame
import random
import math
from scripts.assets import Assets

GRASS_WIDTH = 20
LIGHT_LEVELS = 8
MAX_ROT = 70
PADDING = 20
GPR = PADDING / GRASS_WIDTH

DIR = {'left' : -1, 'right' : 1}


class GrassTile:

    def __init__(self, pos, grass_count=20):
        self.pos = pos

        self.grass : dict[str, Grass] = {}

        self.assets = Assets().assets

        self.tile_img = pygame.Surface((GRASS_WIDTH + PADDING, GRASS_WIDTH + PADDING), pygame.SRCALPHA)
        self.current_count = 0
        self.available_x_pos = [i for i in range(GRASS_WIDTH)]
        self.available_y_pos = [i for i in range(GRASS_WIDTH)]

        for i in range(grass_count):
            self.add_blade()
        
    def add_blade(self, grass_data={}):
        if not len(grass_data):

            x = random.choice(self.available_x_pos)
            self.available_x_pos.remove(x)

            y = random.choice(self.available_y_pos)
            self.available_y_pos.remove(y)

            grass_type = random.randint(0, len(self.assets['img']['grass']) - 1)

            key = f'{x} ; {y} ; {grass_type}'

            self.grass[key] = Grass((x, y), grass_type, grass_tile=self)
        else:
            self.grass[grass_data['KEY']] = Grass(grass_data['POS'], grass_data['TYPE'], grass_tile=self)
            
        self.current_count += 1

    def update_blades(self, dt = 0, wind_force = 10):

        for grass in self.grass.values():
            grass.update(dt, wind_force=wind_force)

    def render_blades(self, surf : pygame.Surface):

        for grass in self.grass.values():
            grass.render(surf)

    def update(self, dt = 0, wind_force = 10):
        self.tile_img.fill((0, 0, 0, 0))

        self.update_blades(dt, wind_force=wind_force)
    
    def render(self, surf : pygame.Surface, render_scroll=(0, 0)):
        
        self.render_blades(self.tile_img)
        surf.blit(self.tile_img, (self.pos[0] - render_scroll[0], self.pos[1] - render_scroll[1]))

class Grass:
    def __init__(self, pos=(0, 0), type=-1, grass_tile : GrassTile = None):
        self.current_count = 0
        self.grass_tile = grass_tile
        self.assets = Assets().assets

        self.img : pygame.Surface = self.assets['img']['grass'][type]

        self.pos : list = list(pos)
        self.world_pos = [self.grass_tile.pos[0] + self.pos[0], self.grass_tile.pos[1] + self.pos[1]]

        self.at_rest_angle = random.randint(-20, 20)

        self.direction = random.choice([1, -1])
        
        self.touch_force = 0

        self.total_force = 0
        self.current_rot = 0

    def rect(self):
        return pygame.Rect(*self.world_pos, *self.img.get_size())
    
    def update(self, dt = 0, wind_force = 10):
        
        if wind_force > 0:
            self.current_rot = min(MAX_ROT, self.current_rot + wind_force * dt)
        else:
            self.current_rot = max(-MAX_ROT, self.current_rot + wind_force * dt)

        if wind_force == 0:
            if self.current_rot > 0 :
                self.current_rot = max(self.at_rest_angle, self.current_rot - MAX_ROT * 2 * dt)
            else:
                self.current_rot = min(self.at_rest_angle, self.current_rot + MAX_ROT * 2 * dt)

    def set_touch_rot(self, dir, dt):
        if dir == "left":
            self.current_rot = self.current_rot = min(MAX_ROT, self.current_rot + MAX_ROT * 10 * dt)
        elif dir == "right":
            self.current_rot = self.current_rot = max(-MAX_ROT, self.current_rot - MAX_ROT * 10 * dt)
        
    def render(self, surf : pygame.Surface):

        img = pygame.transform.rotate(self.img, self.current_rot)
        img_rect = img.get_rect(center=(self.pos[0] + math.cos(math.radians(self.current_rot)), self.pos[1] + math.sin(math.radians(self.current_rot))))

        surf.blit(img, (img_rect[0] + PADDING // 2, img_rect[1] + PADDING // 2))


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
        
