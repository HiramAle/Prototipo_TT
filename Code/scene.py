from __future__ import annotations
import pygame
import json
from player import Player
from pytmx import load_pygame, TiledMap, TiledTileLayer
from typing import Optional
from sprites import Generic, Interaction, Tile
from constants import BG_COLOR
from os.path import exists


class Scene:
    def __init__(self, display: pygame.Surface, player: Optional[Player], name: str, data: dict,
                 manager: SceneManager) -> None:
        # Save parameters
        self.name = name
        self.display = display
        self.manager = manager
        # Import data
        self.data = data
        self.tmx = TiledMap()
        # Sprites
        self.allSprites = CameraGroup(display, self.data["layers"])
        self.collisionSprites = pygame.sprite.Group()
        self.interactionSprites = pygame.sprite.Group()
        Generic((0, 0), pygame.image.load(self.data["bg_image_path"]), self.data["layers"]["Background"]["index"],
                self.allSprites)
        if player:
            self.player = player

    def set_player(self):
        self.player.collisionSprites = self.collisionSprites
        self.player.interactionSprites = self.interactionSprites
        self.player.z = self.data["layers"]["main"]["index"]
        self.allSprites.add(self.player)

    def setup(self) -> None:
        ...

    def event_loop(self, event: pygame.event.Event) -> None:
        self.player.input(event)

    def render(self, dt: float) -> None:
        ...

    def load_data(self) -> None:
        """
        Save the scene data from the json file, into a dictionary.
        """
        with open(f"../Data/Scenes/{self.name}.json", "r") as data:
            self.data = json.load(data)

    def load_tmx(self) -> None:
        if exists(self.data["tmx_path"]):
            self.tmx = load_pygame(self.data["tmx_path"])


class MainScene(Scene):
    def __init__(self, display: pygame.surface, data: dict, manager: SceneManager):
        super().__init__(display, None, "main_scene", data, manager)
        self.load_tmx()
        self.setup()
        self.player = Player((200, 200), self.manager, self.data["layers"]["main"]["index"],
                             self.collisionSprites,
                             self.interactionSprites,
                             self.allSprites)

    def setup(self) -> None:
        for obj in self.tmx.objects:
            position = obj.x, obj.y
            if obj.__getattribute__("class") in "Building":
                Generic(position, obj.image, self.data["layers"]["main"]["index"], self.allSprites,
                        self.collisionSprites)
            if obj.__getattribute__("class") in "Trigger":
                print(f"{obj.name}, {position}, {obj.width},{obj.height}")
                Interaction(position, obj.name, self.data["interactive"][obj.name]["type"],
                            self.data["interactive"][obj.name]["action"], (obj.width, obj.height),
                            self.interactionSprites)

    def render(self, dt: float) -> None:
        self.display.fill(BG_COLOR)
        self.allSprites.update(dt)
        self.allSprites.custom_draw(self.player)


class PlayableScene(Scene):
    def __init__(self, display: pygame.surface, player: Player, name: str, data: dict, manager: SceneManager):
        super().__init__(display, player, name, data, manager)
        self.load_tmx()
        self.set_player()

        for obj in self.tmx.objects:
            position = obj.x, obj.y
            if obj.__getattribute__("class") in "Trigger":
                print(f"{obj.name}, {position}, {obj.width},{obj.height}")
                Interaction(position, obj.name, self.data["interactive"][obj.name]["type"],
                            self.data["interactive"][obj.name]["action"], (obj.width, obj.height),
                            self.interactionSprites)

        for layer in self.tmx.visible_layers:
            if isinstance(layer, TiledTileLayer):
                layer: TiledTileLayer
                for x, y, surface in layer.tiles():
                    pos = (x * 64, y * 64)
                    layer_data = self.data["layers"][layer.name]
                    groups = self.allSprites if not layer_data["collision"] else [self.allSprites,
                                                                                  self.collisionSprites]
                    Tile(surface, pos, layer_data["index"], groups)

        self.player.position = self.tmx.get_object_by_name("Player")

    def render(self, dt: float) -> None:
        self.display.fill(BG_COLOR)
        self.allSprites.update(dt)
        self.allSprites.custom_draw(self.player)


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

        lay = []

        for value in self.layers.values():
            value: dict
            lay.append(value["index"])

        for layer in lay:
            for sprite in sorted(self.sprites(), key=lambda l: l.rect.centery):
                sprite: Generic
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display.blit(sprite.image, offset_rect)


class SceneManager:
    def __init__(self, display: pygame.Surface):
        self.display = display
        self.sceneData = dict
        with open(f"../Data/Scenes/main_scene.json", "r") as data:
            self.sceneData = json.load(data)
        self.sceneStack: list[Scene] = [MainScene(display, self.sceneData, self)]

    def enter_playable_scene(self, name: str):
        with open(f"../Data/Scenes/{name}.json", "r") as data:
            self.sceneData = json.load(data)
        if self.sceneData["class"] == "PlayableScene":
            scene = PlayableScene(self.display, self.sceneStack[-1].player, name, self.sceneData, self)
            self.sceneStack.append(scene)

    def exit_level(self):
        if self.sceneStack:
            self.sceneStack.pop()
        self.sceneStack[-1].set_player()

    def render(self, dt: float):
        if self.sceneStack:
            self.sceneStack[-1].render(dt)

    def event_loop(self, event: pygame.event.Event):
        if self.sceneStack:
            self.sceneStack[-1].event_loop(event)
