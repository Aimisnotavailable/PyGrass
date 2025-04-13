import pygame
import random
import math

GRASS_WIDTH = 7
LIGHT_LEVELS = 8
MAX_ROT = 50
DIR = {'left' : -1, 'right' : 1}


class Grass:
    def __init__(self, pos=(0, 0), color=(0, 255, 0),  flower = False, height=20):
        self.pos : list = list(pos)
        self.height = height

        self.at_rest_angle = random.randint(-20, 20)

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
                self.current_rot = max(self.at_rest_angle, self.current_rot - MAX_ROT * 2 * dt)
            else:
                self.current_rot = min(self.at_rest_angle, self.current_rot + MAX_ROT * 2 * dt)

    def set_touch_rot(self, dir, dt):
        if dir == "left":
            self.current_rot = self.current_rot = min(MAX_ROT, self.current_rot + MAX_ROT * 3 * dt)
        elif dir == "right":
            self.current_rot = self.current_rot = max(-MAX_ROT, self.current_rot - MAX_ROT * 3 * dt)
        
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
        
