from __future__ import annotations
import pygame
import json
from support import import_cut_graphics
from constants import TILE_SIZE


class Actor(pygame.sprite.Sprite):
    def __init__(self, position: tuple, name: str, z: int, collision_sprites: pygame.sprite.Group,
                 *groups: pygame.sprite.Group):
        super().__init__(*groups)
        # Data
        self.data = {}
        self.name = name
        self.load_data()
        # Assets
        self.animations = {}
        self.import_assets()
        self.frameIndex = 0
        self.animationSpeed = 9
        self.status = "right_idle"
        self.image = self.animations[self.status][self.frameIndex]
        # Movement
        self.rect = self.image.get_rect()
        self.position = pygame.math.Vector2(position)
        self.hitbox = self.rect.copy().inflate(-10, -10)
        self.hitbox.midbottom = self.rect.midbottom
        self.direction = pygame.math.Vector2()
        self.baseSpeed = 300
        self.z = z
        # Collision
        self.collisionSprites = collision_sprites

    def load_data(self):
        with open(f"../Data/Actors/{self.name}.json", "r") as data:
            self.data = json.load(data)

    def import_assets(self):
        self.animations = {"left_walk": [], "right_walk": [],
                           "left_idle": [], "right_idle": []}

        for animation in self.animations.keys():
            full_path = f"{self.data['assets_path']}" + animation + ".png"
            self.animations[animation] = import_cut_graphics(full_path, TILE_SIZE, TILE_SIZE * 2)

    def animate(self, dt: float):
        self.frameIndex += self.animationSpeed * dt
        if self.frameIndex >= len(self.animations[self.status]):
            self.frameIndex = 0
        self.image = self.animations[self.status][int(self.frameIndex)]

    def set_status(self):
        if self.direction.magnitude() == 0 and not ("idle" in self.status):
            self.status = self.status.split("_")[0] + "_idle"

    def collision(self, direction: str):
        for sprite in self.collisionSprites.sprites():
            sprite: Actor
            if sprite.hitbox.colliderect(self.hitbox):
                if direction == "horizontal":
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                    self.rect.midbottom = self.hitbox.midbottom
                    self.position.x = self.rect.centerx
                if direction == "vertical":
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom
                    self.rect.midbottom = self.hitbox.midbottom
                    self.position.y = self.rect.centery

    def move(self, dt: float):
        # Normalizing direction vector
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # Horizontal movement
        self.position.x += self.direction.x * self.baseSpeed * dt
        self.rect.centerx = round(self.position.x)
        self.hitbox.midbottom = self.rect.midbottom
        self.collision("horizontal")

        # Vertical movement
        self.position.y += self.direction.y * self.baseSpeed * dt
        self.rect.centery = round(self.position.y)
        self.hitbox.midbottom = self.rect.midbottom
        self.collision("vertical")

    def update(self, dt: float):
        ...
