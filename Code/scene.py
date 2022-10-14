from __future__ import annotations
import pygame
import json
from player import Player
from pytmx import load_pygame, TiledMap
from typing import Optional
from sprites import Generic, Interaction
from constants import BG_COLOR


class Scene:
    def __init__(self, display: pygame.Surface, player: Optional[Player], name: str, manager: SceneManager) -> None:
        # Import data
        self.name = name
        self.data = {}
        self.load_data()
        self.tmx = TiledMap()
        self.load_tmx()
        # Attributes
        self.display = display
        self.player = player
        self.manager = manager
        # Sprites
        self.allSprites = CameraGroup(display, self.data["layers"])
        self.collisionSprites = pygame.sprite.Group()
        self.interactionSprites = pygame.sprite.Group()
        Generic((0, 0), pygame.image.load(self.data["bg_image_path"]), self.data["layers"]["floor"], self.allSprites)

    def setup(self) -> None: ...

    def event_loop(self, event: pygame.event.Event) -> None: ...

    def render(self, dt: float) -> None: ...

    def load_data(self) -> None:
        """
        Save the scene data from the json file, into a dictionary.
        """
        with open(f"../Data/Scenes/{self.name}.json", "r") as data:
            self.data = json.load(data)

    def load_tmx(self) -> None:
        self.tmx = load_pygame(self.data["tmx_path"])


class MainScene(Scene):
    def __init__(self, display: pygame.surface, manager: SceneManager):
        super().__init__(display, None, "main_scene", manager)
        self.setup()
        self.player = Player((200, 200), self.manager.enter_level, self.collisionSprites, self.interactionSprites,
                             self.allSprites)

    def setup(self) -> None:
        for obj in self.tmx.objects:
            position = obj.x, obj.y
            if obj.__getattribute__("class") in "Building":
                Generic(position, obj.image, self.data["layers"]["main"], self.allSprites, self.collisionSprites)
            if obj.__getattribute__("class") in "Trigger":
                print(f"{obj.name}, {position}, {obj.width},{obj.height}")
                Interaction(position, obj.name, self.data["interactive"][obj.name]["type"],
                            self.data["interactive"][obj.name]["action"], (obj.width, obj.height),
                            self.interactionSprites)
                print(self.interactionSprites)

    def render(self, dt: float) -> None:
        self.display.fill(BG_COLOR)
        self.allSprites.update(dt)
        self.allSprites.custom_draw(self.player)


class TestScene(Scene):
    def __init__(self, display: pygame.Surface, player, name: str, manager: SceneManager):
        super().__init__(display, player, name, manager)
        print(player.collisionSprites)
        print(player.interactionSprites)

    def render(self, dt: float):
        self.display.fill(self.data["color"])

    def event_loop(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            for trigger in self.data["triggers"].values():
                trigger: dict
                if keys[eval(trigger["key"])]:
                    self.manager.enter_level(trigger["level"])


class CameraGroup(pygame.sprite.Group):
    def __init__(self, display: pygame.Surface, layers: dict):
        super().__init__()
        self.display = display
        self.offset = pygame.math.Vector2()
        self.width = display.get_width()
        self.height = display.get_height()
        self.layers = layers

    def custom_draw(self, player: Player):
        self.offset.x = player.rect.centerx - self.width / 2
        self.offset.y = player.rect.centery - self.height / 2

        for layer in self.layers.values():
            for sprite in sorted(self.sprites(), key=lambda l: l.rect.centery):
                sprite: Generic
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display.blit(sprite.image, offset_rect)


class SceneManager:
    def __init__(self, display: pygame.Surface):
        self.display = display
        self.sceneStack: list[Scene] = [MainScene(display, self)]

    def enter_level(self, name: str):
        scene = TestScene(self.display, self.sceneStack[-1].player, name, self)
        self.sceneStack.append(scene)

    def exit_level(self):
        if self.sceneStack:
            self.sceneStack.pop()

    def render(self, dt: float):
        if self.sceneStack:
            self.sceneStack[-1].render(dt)

    def event_loop(self, event: pygame.event.Event):
        if self.sceneStack:
            self.sceneStack[-1].event_loop(event)
