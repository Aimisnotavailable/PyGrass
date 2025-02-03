import pygame
import sys
import random
import math
from scripts.engine import Engine
from scripts.camera import Follow

GRASS_WIDTH = 8
LIGHT_LEVELS = 8
MAX_ROT = 70

RESISTANCE = 20

BOUNDARY_KEYS = {"left_wind" : (0, 1, 1), "right_wind" : (1, 0, -1), "default" : (0, 1, 1)}

class Grass:
    def __init__(self, pos=(0, 0), color=(0, 255, 0), flower = False, height=20):
        self.pos : list = list(pos)
        self.height = height

        self.direction = random.choice([1, -1])
        self.main_leaf_points = [[GRASS_WIDTH // 5, self.height * 0.6], [GRASS_WIDTH // 2, 0], [GRASS_WIDTH * 0.8, self.height * 0.6], [GRASS_WIDTH // 3, self.height * 1]]
        self.stem_points = [[GRASS_WIDTH // 5, self.height * 0.6], [GRASS_WIDTH // 3, self.height * 1], [GRASS_WIDTH * 0.8, self.height * 0.6]]
        self.flower_points = [[GRASS_WIDTH // 5, self.height * 0.4], [GRASS_WIDTH // 2, 0], [GRASS_WIDTH * 0.8, self.height * 0.4]]

        self.img = pygame.Surface((GRASS_WIDTH, self.height), pygame.SRCALPHA)
        self.angle = 0
        # self.img = pygame.transform.rotate(self.img, self.angle)
        self.touch_force = 0

        self.img.fill((0, 0, 0, 0))
        pygame.draw.polygon(self.img, color, self.main_leaf_points)
        pygame.draw.polygon(self.img, (0, 120, 0), self.stem_points)

        self.total_force = 0
        if flower:
            pygame.draw.polygon(self.img, (255, 255, 0), self.flower_points)

        # for points in self.main_leaf_points:
        #     pygame.draw.circle(self.img, (255, 255, 255), points, 1)

    def set_touch_force(self, dir):
        self.touch_force = 200 if dir == "left" else -200

    def rect(self):
        return pygame.Rect(*self.pos, *self.img.get_size())
    
    def update(self, dt, force=0):
        
        self.total_force  = force * dt + self.touch_force * dt

        if self.total_force > 0:
            self.angle = min(MAX_ROT, self.angle + self.total_force)
        else:
            self.angle = max(-MAX_ROT, self.angle + self.total_force)

        if self.touch_force > 0:
            self.touch_force = max(0, self.touch_force - 400 * dt)
        else:
            self.touch_force = min(self.touch_force + 400 * dt, 0)

        if self.total_force > 0:
            self.angle = max(0, self.angle - RESISTANCE * dt)
        elif self.total_force < 0:
            self.angle = min(0, self.angle + RESISTANCE * dt)
        
        
    def render(self, color, surf : pygame.Surface, render_scroll=(0, 0)):

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

        self.mouse_surf = pygame.Surface((40, 40))

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

            m_rect = self.mouse_surf.get_rect(center=[mpos[0] + render_scroll[0], mpos[1] + render_scroll[1]])

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
                pos = m_rect.center
                g_pos = f"{pos[0]//GRASS_WIDTH} ; {pos[1]//GRASS_WIDTH}"
                
                if g_pos not in self.grass:
                    self.grass[g_pos] = Grass(((pos[0]//GRASS_WIDTH) * GRASS_WIDTH, (pos[1]//GRASS_WIDTH) * GRASS_WIDTH), (0, random.randint(190, 255), 0), True if random.randint(0, 100) < 12 else False, random.randint(20, 30)) 
            
            # WORLD GRID POSITIONS
            world_boundary_x = [render_scroll[0] // GRASS_WIDTH - GRASS_WIDTH, (render_scroll[0] + self.display.get_width()) // GRASS_WIDTH + GRASS_WIDTH]
            world_boundary_y = [render_scroll[1] // GRASS_WIDTH - GRASS_WIDTH, (render_scroll[1] + self.display.get_height()) // GRASS_WIDTH + GRASS_WIDTH]
            world_size = [world_boundary_x[1] - world_boundary_x[0], world_boundary_y[1] - world_boundary_y[0]]

            grass_nearby = []

            dir = "right_wind" if self.force < 0 else "left_wind"
            
            if (int(abs(self.force)) <= 2.5 and self.force < RESISTANCE) or abs(self.force) > 100 * 0.8 :
                dir = "default"

            boundary_values = BOUNDARY_KEYS[dir]

            for x in range(world_boundary_x[boundary_values[0]], world_boundary_x[boundary_values[1]], boundary_values[2]):
                for y in range(world_boundary_y[boundary_values[0]], world_boundary_y[boundary_values[1]], boundary_values[2]):
                    g_pos = f"{x} ; {y}"
                    if g_pos in self.grass:

                        grass : Grass = self.grass[g_pos]
                        
                        grass_nearby.append(grass)
                        saturation = abs((world_boundary_y[0] - y) / (world_size[1] / LIGHT_LEVELS)) / LIGHT_LEVELS

                        if saturation < 0.5:
                            saturation = 1 - saturation

                        # if (abs(world_boundary_x[0] - x) > int(world_size[0] * 0.5) or abs(world_boundary_x[0] - x) < int(world_size[0] *  0.4)) or (abs(world_boundary_y[0] - y) > int(world_size[1] * 0.5) or abs(world_boundary_y[0] - y) < int(world_size[1] *  0.4)):
                        #     saturation += 0.1

                        saturation -= 0.3

                        grass.render((0, min(max(15, int(255 * saturation)), 255), 0), self.display, render_scroll)

                        grass_rect = grass.rect()
                        
                        if m_rect.colliderect(grass_rect):
                            if (m_rect[0] + m_rect[2] // 2) <= grass_rect[0]:
                                dir = 'right'
                            else:
                                dir = 'left'

                            grass.set_touch_force(dir=dir)

                        grass.update(dt, self.force)
            
            # for grass in grass_nearby:
                
            
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