import pygame
import sys
import random
import math
from scripts.engine import Engine
from scripts.camera import Follow

GRASS_WIDTH = 8
LIGHT_LEVELS = 8
MAX_ROT = 40

RESISTANCE = 20

class Grass:
    def __init__(self, pos=(0, 0), height=20):
        self.pos : list = list(pos)
        self.height = height

        self.direction = random.choice([1, -1])
        self.points = [[GRASS_WIDTH // 5, self.height * 0.6], [GRASS_WIDTH // 2, 0], [GRASS_WIDTH * 0.8, self.height * 0.6], [GRASS_WIDTH // 3, self.height * 1.5]]
        self.img = pygame.Surface((GRASS_WIDTH, self.height), pygame.SRCALPHA)
        self.angle = 0
        # self.img = pygame.transform.rotate(self.img, self.angle)

    def rect(self):
        return pygame.Rect(*self.pos, *self.img.get_size())
    def update(self, dt, force=0):
        self.angle = max(-MAX_ROT, min(MAX_ROT, self.angle + force * dt))

        if force > 0:
            self.angle = max(0, self.angle - RESISTANCE * dt)
        elif force < 0:
            self.angle = min(0, self.angle + RESISTANCE * dt)
        
        
    def render(self, color, surf : pygame.Surface, render_scroll=(0, 0)):
        self.img.fill((0, 0, 0, 0))
        pygame.draw.polygon(self.img, color, self.points)

        img = pygame.transform.rotate(self.img, self.angle)
        img_rect = img.get_rect(center=(self.pos[0] + math.cos(math.radians(self.angle)) * 1 - render_scroll[0], self.pos[1] + math.sin(math.radians(self.angle)) * 1 - render_scroll[1]))

        surf.blit(img, img_rect)

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
                self.mouse_offset[1] += 100 * dt
            elif mpos[1] <= 5:
                self.mouse_offset[1] -= 100 * dt

            render_scroll = self.camera.scroll(self.display, dt, (mpos[0] + self.mouse_offset[0], mpos[1] + self.mouse_offset[1]))
            if not int(self.force):
                self.force = random.choice([100, -100])

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
                pos = [(mpos[0] + render_scroll[0]), (mpos[1] + render_scroll[1])]
                g_pos = f"{pos[0]//GRASS_WIDTH} ; {pos[1]//GRASS_WIDTH}"
                
                if g_pos not in self.grass:
                    self.grass[g_pos] = Grass(((pos[0]//GRASS_WIDTH) * GRASS_WIDTH, (pos[1]//GRASS_WIDTH) * GRASS_WIDTH)) 
            
            # WORLD GRID POSITIONS
            world_boundary_x = [render_scroll[0] // GRASS_WIDTH - GRASS_WIDTH, (render_scroll[0] + self.display.get_width()) // GRASS_WIDTH + GRASS_WIDTH]
            world_boundary_y = [render_scroll[1] // GRASS_WIDTH - GRASS_WIDTH, (render_scroll[1] + self.display.get_height()) // GRASS_WIDTH + GRASS_WIDTH]
            world_size = [world_boundary_x[1] - world_boundary_x[0], world_boundary_y[1] - world_boundary_y[0]]

            for x in range(world_boundary_x[0], world_boundary_x[1]):
                for y in range(world_boundary_y[0], world_boundary_y[1]):
                    g_pos = f"{x} ; {y}"
                    if g_pos in self.grass:
                        grass : Grass = self.grass[g_pos]
                        
                        saturation = abs((world_boundary_y[0] - y) / (world_size[1] / LIGHT_LEVELS)) / LIGHT_LEVELS

                        if saturation < 0.5:
                            saturation = 1 - saturation

                        # if (abs(world_boundary_x[0] - x) > int(world_size[0] * 0.5) or abs(world_boundary_x[0] - x) < int(world_size[0] *  0.4)) or (abs(world_boundary_y[0] - y) > int(world_size[1] * 0.5) or abs(world_boundary_y[0] - y) < int(world_size[1] *  0.4)):
                        #     saturation += 0.1

                        saturation -= 0.3

                        grass.render((0, min(max(15, int(255 * saturation)), 255), 0), self.display, render_scroll)
                        
                        m_pos_c = [mpos[0] + render_scroll[0], mpos[1] + render_scroll[1]]
                        m_rect = pygame.Rect(*m_pos_c, 10, 10)

                        if m_rect.colliderect(grass.rect()):
                            grass.update(dt, 200)
                        else:
                            grass.update(dt, self.force)
            
            if self.force > 0:
                self.force = max(0, self.force - (self.force * dt))
            elif self.force < 0:
                self.force = min(0, self.force - (self.force * dt))

            pygame.draw.circle(self.display, (255, 255, 255), mpos, 10, 1)

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 0), unsetcolor=(0, 0, 0, 0))

            for offset in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
                self.display_2.blit(display_sillhouette, offset)
            
            self.display_2.blit(self.display)
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), (0, 0))

            pygame.display.update()
            # self.clock.tick(60)

Window().run()