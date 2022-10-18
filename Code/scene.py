from __future__ import annotations
import pygame
import json
from player import Player
from pytmx import load_pygame, TiledMap, TiledTileLayer
from typing import Optional
from sprites import Generic, Interaction, Tile, Cable, ColorLine, ColorLineCursor
from constants import BG_COLOR, BLUE
from os.path import exists
import random
from overlay import Overlay
from buttons import Button


class Scene:
    def __init__(self, display: pygame.Surface, player_inventory: Optional[dict], name: str, data: dict,
                 manager: SceneManager) -> None:
        # Save parameters
        self.name = name
        self.display = display
        self.manager = manager
        # Import data
        self.data = data
        self.tmx = TiledMap()
        # Sprites
        self.collisionSprites = pygame.sprite.Group()
        self.interactionSprites = pygame.sprite.Group()
        if "layers" in self.data.keys():
            self.allSprites = CameraGroup(display, self.data["layers"])
            self.player = Player(None, self.manager, self.data["layers"]["main"]["index"], self.collisionSprites,
                                 self.interactionSprites, self.allSprites)
        else:
            self.allSprites = pygame.sprite.Group()
            self.player = Player(None, self.manager, 1, self.collisionSprites, self.interactionSprites, self.allSprites)

        if self.data["bg_image_path"] != "":
            Generic((0, 0), pygame.image.load(self.data["bg_image_path"]), self.data["layers"]["Background"]["index"],
                    self.allSprites)

        if player_inventory:
            self.player.itemInventory = player_inventory

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
        self.overlay = Overlay(self.player, self.display)

    def setup(self) -> None:
        for obj in self.tmx.objects:
            position = obj.x, obj.y
            if obj.__getattribute__("class") in "Building":
                Generic(position, obj.image, self.data["layers"]["main"]["index"], self.allSprites,
                        self.collisionSprites)
            if obj.__getattribute__("class") in "Trigger":
                Interaction(position, obj.name, self.data["interactive"][obj.name]["type"],
                            self.data["interactive"][obj.name]["action"], (obj.width, obj.height),
                            self.interactionSprites)

    def render(self, dt: float) -> None:
        self.display.fill(BG_COLOR)
        self.allSprites.update(dt)
        self.allSprites.custom_draw(self.player)
        self.overlay.display()


class PlayableScene(Scene):
    def __init__(self, display: pygame.surface, player_inventory: dict, name: str, data: dict, manager: SceneManager):
        super().__init__(display, player_inventory, name, data, manager)
        self.load_tmx()
        self.overlay = Overlay(self.player, self.display)
        for obj in self.tmx.objects:
            position = obj.x, obj.y
            if obj.__getattribute__("class") in "Trigger":
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
        self.overlay.display()


class CableScene(Scene):
    def __init__(self, display: pygame.surface.Surface, player_inventory: dict, data: dict, manager):
        super().__init__(display, player_inventory, "cable", data, manager)
        self.standards = self.data["standards"]
        self.cableOrder = self.standards["T568A"]
        self.allSprites = pygame.sprite.Group()
        self.barSprites = pygame.sprite.Group()
        self.dragging = False
        self.selectedCable = None
        self.mouse_offset = 0
        self.ordered = False
        self.setup()

    def setup(self):
        # Randomize cable order
        random.shuffle(self.cableOrder)
        # Set cable position
        start_pos = 200
        increase_amount = 50
        for i, cableName in enumerate(self.cableOrder):
            position = (int(self.display.get_width() / 2), start_pos + (i * increase_amount))
            assets_path = self.data["cable_sprites_path"]
            if cableName[0] == "p":
                assets_path += "Plain"
            else:
                assets_path += "Strip"
            assets_path += "_" + cableName[1:] + ".png"
            image = pygame.image.load(assets_path).convert_alpha()
            Cable(position, cableName, image, self.allSprites)

        # ImageButton((self.gameCanvas.get_width() / 2, self.gameCanvas.get_height() - 100), "Assets/Images/Pin.png",
        #             self.barSprites)
        colors = pygame.image.load("../Assets/Scenes/CableScene/LineColor.png").convert_alpha()
        cursor = pygame.image.load("../Assets/Scenes/CableScene/ColorCursor.png").convert_alpha()

        ColorLineCursor((self.display.get_width() / 2, 100), cursor,
                        ColorLine((self.display.get_width() / 2, 100), colors, self.barSprites), self.barSprites)

    def check_cable_order(self):
        for standard in self.standards:
            if self.standards[standard] == self.cableOrder:
                self.ordered = True

    def drag_start(self, event: pygame.event.Event):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for cable in self.allSprites:
            if isinstance(cable, Cable):
                if cable.rect.collidepoint(mouse_x, mouse_y):

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.dragging = True
                        self.mouse_offset = mouse_y - cable.rect.y
                        self.selectedCable = cable

    def drag_end(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONUP and self.selectedCable:
            if self.dragging:
                self.dragging = False
                self.selectedCable.rect.centery = self.selectedCable.position.y
                self.check_cable_order()
                self.selectedCable = None

    def on_dragging(self):
        if self.dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.selectedCable.rect.y = mouse_y - self.mouse_offset

            for cable in self.allSprites:
                if isinstance(cable, Cable):
                    if cable != self.selectedCable:
                        if cable.hitbox.collidepoint(mouse_x, mouse_y):
                            cable.rect.centery = self.selectedCable.position.y
                            i1 = self.cableOrder.index(cable.name)
                            i2 = self.cableOrder.index(self.selectedCable.name)

                            self.cableOrder[i1], self.cableOrder[i2] = self.cableOrder[i2], self.cableOrder[i1]
                            cable.position, self.selectedCable.position = self.selectedCable.position, cable.position

    def event_loop(self, event: pygame.event.Event):
        self.allSprites.update()
        if self.ordered:
            self.barSprites.update()
            for sprite in self.barSprites:
                if isinstance(sprite, ColorLineCursor):
                    quality = sprite.check_cursor(event)
                    if quality:
                        # self.player.itemInventory["cable"].append(CableItem("T568A", 5, quality))
                        self.player.add_item("money", 10)
                        self.manager.exit_level()

        self.drag_start(event)
        self.on_dragging()
        self.drag_end(event)

    def render(self, dt: float):
        self.display.fill("#1e1e1e")
        self.allSprites.draw(self.display)
        if self.ordered:
            self.barSprites.draw(self.display)
            for sprite in self.barSprites:
                if isinstance(sprite, ColorLineCursor):
                    sprite.animate(dt)


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
        self.sceneStack: list[Scene] = []
        # overlay image
        self.image = pygame.Surface((display.get_width(), display.get_height()))
        self.color = 255
        self.speed = -4
        self.name = ""
        self.start = False
        self.enter = False
        self.exit = False

    def change_scene(self):
        if self.name == "exit":
            pygame.quit()
            exit()

        if self.enter:
            with open(f"../Data/Scenes/{self.name}.json", "r") as data:
                self.sceneData = json.load(data)
            if self.sceneData["class"] == "MainScene":
                scene = MainScene(self.display, self.sceneData, self)
            if self.sceneData["class"] == "PlayableScene":
                scene = PlayableScene(self.display, self.sceneStack[-1].player.itemInventory, self.name, self.sceneData,
                                      self)
            if self.sceneData["class"] == "CableScene":
                scene = CableScene(self.display, self.sceneStack[-1].player.itemInventory, self.sceneData, self)
            if self.sceneData["class"] == "Menu":
                scene = Menu(self.display, self.sceneData, self)

            self.sceneStack.append(scene)
        if self.exit:
            self.sceneStack[-2].player.itemInventory = self.sceneStack[-1].player.itemInventory
            if self.sceneStack:
                self.sceneStack.pop()

    def enter_scene(self, name: str):
        self.name = name
        if name == "exit":
            self.change_scene()
        self.start = True
        self.enter = True

    def fade(self):
        self.color += self.speed
        if self.color <= 0:
            self.speed *= -1
            self.color = 0
            self.change_scene()
        if self.color > 255:
            self.color = 255
            self.speed = -4
            self.start = False
            self.enter = False
            self.exit = False

        self.image.fill((self.color, self.color, self.color))
        self.display.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def exit_level(self):
        self.start = True
        self.exit = True

    def render(self, dt: float):
        if self.sceneStack:
            self.sceneStack[-1].render(dt)
        if self.start:
            self.fade()

    def event_loop(self, event: pygame.event.Event):
        if self.sceneStack:
            self.sceneStack[-1].event_loop(event)


class Menu(Scene):
    def __init__(self, display: pygame.surface, data: dict, manager: SceneManager):
        super().__init__(display, None, "main_menu", data, manager)
        self.buttons = pygame.sprite.Group()
        self.buttonsData = self.data["buttons"]
        Button((self.display.get_width() / 2, 400), "Play", "orange", self.buttons)
        Button((self.display.get_width() / 2, 500), "Options", "orange", self.buttons)
        Button((self.display.get_width() / 2, 600), "Exit", "orange", self.buttons)

    def event_loop(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.buttons:
                button: Button
                if button.hover():
                    self.manager.enter_scene(self.buttonsData[button.text]["action"])

    def render(self, dt: float) -> None:
        self.display.fill(BLUE)
        self.buttons.update(dt)
        self.buttons.draw(self.display)
