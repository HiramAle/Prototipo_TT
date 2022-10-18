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


class Tile(Generic):
    def __init__(self, surface: pygame.Surface, position: tuple, z: int, *groups: pygame.sprite.Group):
        super().__init__(position, surface, z, *groups)
        self.hitbox = self.rect.copy()


class Cable(Generic):
    def __init__(self, position: tuple, name: str, surface: pygame.Surface, *groups: pygame.sprite.Group):
        super().__init__(position, surface, 1, *groups)
        self.position = pygame.math.Vector2(position)
        self.name = name
        self.image = surface
        self.rect = self.image.get_rect(center=position)
        self.hitbox = self.rect.copy().inflate(0, -10)

    def update(self):
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.centery = self.rect.centery


class ColorLine(Generic):
    def __init__(self, position: tuple, surface: pygame.Surface, *groups: pygame.sprite.Group):
        super().__init__(position, surface, 1, *groups)
        self.image = surface
        self.rect = self.image.get_rect(center=position)
        self.orangeHitbox = self.rect.inflate(-25, 0)
        self.yellowHitbox = self.rect.inflate(-150, 0)
        self.greenHitbox = self.rect.inflate(-230, 0)


class ColorLineCursor(Generic):
    def __init__(self, position: tuple, surface: pygame.Surface, color_line: ColorLine, *groups: pygame.sprite.Group):
        super().__init__(position, surface, 1, *groups)

        self.image = surface
        self.rect = self.image.get_rect(center=position)
        self.hitbox = self.rect.copy().inflate(-30, -10)
        self.position = pygame.math.Vector2(position)
        self.direction = "left"
        self.origin = position
        self.colorLine = color_line
        self.leftLimit = self.colorLine.rect.left
        self.rightLimit = self.colorLine.rect.right
        self.animationSpeed = 300

    def animate(self, dt: float):
        if self.direction == "left":
            if self.rect.left <= self.leftLimit:
                self.direction = "right"
            else:
                self.position.x -= self.animationSpeed * dt
        else:
            if self.rect.right >= self.rightLimit:
                self.direction = "left"
            else:
                self.position.x += self.animationSpeed * dt

        self.rect.centerx = round(self.position.x)
        self.hitbox.centerx = self.rect.centerx

    def check_cursor(self, event: pygame.event.Event):
        quality = None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.hitbox.colliderect(self.colorLine.greenHitbox) and \
                        self.hitbox.colliderect(self.colorLine.yellowHitbox) and \
                        self.hitbox.colliderect(self.colorLine.orangeHitbox):
                    quality = "green"

                if not self.hitbox.colliderect(self.colorLine.greenHitbox) and \
                        self.hitbox.colliderect(self.colorLine.yellowHitbox) and \
                        self.hitbox.colliderect(self.colorLine.orangeHitbox):
                    quality = "yellow"

                if not self.hitbox.colliderect(self.colorLine.greenHitbox) and \
                        not self.hitbox.colliderect(self.colorLine.yellowHitbox) and \
                        self.hitbox.colliderect(self.colorLine.orangeHitbox):
                    quality = "orange"
        return quality
