import pygame
from typing import Union


class Generic(pygame.sprite.Sprite):
    def __init__(self, position: tuple, surface: pygame.Surface, z: int, *groups: pygame.sprite.Group):
        super().__init__(*groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)


class Interaction(Generic):
    def __init__(self, position: tuple, name: str, in_type: str, action: str, size: tuple,
                 *groups: pygame.sprite.Group):
        surface = pygame.Surface(size)
        super().__init__(position, surface, 0, *groups)
        self.name = name
        self.type = in_type
        self.action = action
