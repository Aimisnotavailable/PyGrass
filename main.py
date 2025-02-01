import pygame
import sys
import random
from engine import Engine

GRASS_WIDTH = 10

class Grass:
    def __init__(self, pos=(0, 0), height=35):
        self.pos : list = list(pos)
        self.height = height

        self.direction = random.choice([1, -1])

        self.points = [self.pos.copy(), [self.pos[0] + GRASS_WIDTH / 2, self.pos[1] - height], [self.pos[0] + GRASS_WIDTH, self.pos[1]]]

    def update(self, dt, speed=50):
        self.points[1][0] += (speed * self.direction) * dt

        if self.points[1][0] < self.points[0][0]:
            self.direction = 1
        elif self.points[1][0] > self.points[2][0]:
            self.direction = -1

    def render(self, dt, color, surf : pygame.Surface):
        pygame.draw.polygon(surf, color, self.points)
        self.update(dt)

class Window(Engine):

    def __init__(self):
        super().__init__()

        self.display_2 = pygame.Surface((300, 200))
        self.insert = False
        self.delete = False

        self.grass : dict[str:Grass] = {}


    def run(self):
        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.fill((0, 0, 0))

            dt = (self.clock.tick() / 1000.0) + 1e-5

            mpos = pygame.mouse.get_pos()
            mpos = [mpos[0] // 2, mpos[1] // 2]

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

            if self.insert:
                g_pos = f"{mpos[0]//GRASS_WIDTH} ; {mpos[1]//GRASS_WIDTH}"
                
                if g_pos not in self.grass:
                    self.grass[g_pos] = Grass(((mpos[0]//GRASS_WIDTH) * GRASS_WIDTH, (mpos[1]//GRASS_WIDTH) * GRASS_WIDTH)) 
            
            for x in range(0, self.display.get_width()//GRASS_WIDTH):
                for y in range(0, self.display.get_height()//GRASS_WIDTH):
                    g_pos = f"{x} ; {y}"
                    if g_pos in self.grass:
                        saturation = (GRASS_WIDTH * y / self.display.get_height())
                        self.grass[g_pos].render(dt, (0, min(max(15, int(255 * saturation)), 255), 0), self.display)

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 0), unsetcolor=(0, 0, 0, 0))

            for offset in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
                self.display_2.blit(display_sillhouette, offset)
            
            self.display_2.blit(self.display)
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), (0, 0))

            pygame.display.update()
            #self.clock.tick(60)

Window().run()