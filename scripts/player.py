import pygame

LERP_VALUE = 0.1
RADIUS = 20

class Player:

    def __init__(self, pos, id, game, is_self):
        self.game = game
        self.pos = pos
        self.id = id
        self.rect = pygame.Rect(*self.pos, RADIUS * 2, RADIUS * 2)
        self.is_self = is_self
    
    def update(self, new_pos):
        self.pos = [self.__lerp__(self.pos[0], new_pos[0]), self.__lerp__(self.pos[1], new_pos[1])]

    def render(self, surf : pygame.Surface, offset=[0, 0]):

        self.rect.center = self.pos
        pygame.draw.circle(surf, (255, 255, 255), self.rect.center, RADIUS, 1)

        id_surf = self.game.font.render(self.id, True, (0, 0, 0) if self.is_self else (255, 255, 255))
        id_rect = id_surf.get_rect(center=(self.rect.centerx, self.rect.bottom))
        surf.blit(id_surf, id_rect)

    def __lerp__(self, start, end):
        return start + (end - start) * LERP_VALUE