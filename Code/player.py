import pygame
from actor import Actor
from sprites import Interaction


class Player(Actor):
    def __init__(self, position: tuple, enter_level: callable, collision_sprites: pygame.sprite.Group,
                 interaction_sprites: pygame.sprite.Group,
                 *groups: pygame.sprite.Group):
        super().__init__(position, "Player", collision_sprites, *groups)
        self.load_data()
        self.xp = 0
        self.level = 0
        # Inventory
        self.itemInventory = {
            "money": 500,
            "udp": 0,
            "rj45": 0,
            "cable": []
        }
        self.interactionSprites = interaction_sprites
        self.import_assets()
        self.enterLevel = enter_level

    def input(self):
        keys = pygame.key.get_pressed()
        # Vertical
        if keys[pygame.K_w]:
            self.direction.y = -1
            self.status = self.status.split("_")[0] + "_walk"
        elif keys[pygame.K_s]:
            self.direction.y = 1
            self.status = self.status.split("_")[0] + "_walk"
        else:
            self.direction.y = 0

        # Horizontal
        if keys[pygame.K_a]:
            self.direction.x = -1
            self.status = "left_walk"
        elif keys[pygame.K_d]:
            self.direction.x = 1
            self.status = "right_walk"
        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE]:
            collided_interaction_sprites = pygame.sprite.spritecollide(self, self.interactionSprites, False)
            if collided_interaction_sprites:
                collided_interaction_sprites: [Interaction]
                if collided_interaction_sprites[0].type == "scene":
                    self.enterLevel(collided_interaction_sprites[0].action)
                if collided_interaction_sprites[0].type == "add":
                    self.itemInventory["money"] += collided_interaction_sprites[0].action



    def update(self, dt: float):
        self.input()
        self.set_status()
        self.move(dt)
        self.animate(dt)
