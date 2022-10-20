from __future__ import annotations
import pygame
from constants import BLUE, RED, YELLOW
from dataclasses import dataclass


class Scene:
    def __init__(self, display: pygame.Surface):
        self.display = display
        self.color = ""
        self.transitioning = False
        self.endTransitioning = True
        self.value = 0

    def input(self, manager: SceneManager):
        ...

    def update(self, manager: SceneManager):
        ...

    def draw(self, dt: float):
        self.display.fill(self.color)


class MainMenu(Scene):
    def __init__(self, display: pygame.Surface):
        super().__init__(display)
        self.color = BLUE

    def input(self, manager: SceneManager):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            manager.enter_scene(Transition(self.display, self, GameScene(self.display)))


class GameScene(Scene):
    def __init__(self, display: pygame.Surface):
        super().__init__(display)
        self.color = RED

    def input(self, manager: SceneManager):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            manager.enter_scene(PauseScene(self.display))


class PauseScene(Scene):
    def __init__(self, display: pygame.Surface):
        super().__init__(display)
        self.color = YELLOW

    def input(self, manager: SceneManager):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            manager.exit_scene()
        elif keys[pygame.K_SPACE]:
            manager.set(MainMenu(self.display))


@dataclass
class Actor(pygame.sprite.Sprite):
    color: int = 2


class Transition(Scene):
    def __init__(self, display: pygame.Surface, from_scene: Scene, to_scene: Scene):
        super().__init__(display)
        self.image = pygame.Surface((display.get_width(), display.get_height()))
        self.fromScene = from_scene
        self.toScene = to_scene
        self.speed = -2
        self.colorValue = 255
        self.action = False

    def update(self, manager: SceneManager):
        self.colorValue += self.speed
        if self.colorValue <= 0:
            self.speed *= -1
            self.colorValue = 0
            self.action = True

        if self.colorValue > 255:
            self.colorValue = 255
            manager.exit_scene()
            manager.enter_scene(self.toScene)

        self.image.fill((self.colorValue, self.colorValue, self.colorValue))

    def draw(self, dt: float):
        if not self.action:
            self.fromScene.draw(dt)
        else:
            self.toScene.draw(dt)
        self.display.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


class SceneManager:
    def __init__(self):
        self.stackScene: list[Scene] = []

    def enter_scene(self, scene: Scene):
        self.stackScene.append(scene)

    def exit_scene(self):
        if self.stackScene:
            self.stackScene.pop()

    def input(self):
        if self.stackScene:
            self.stackScene[-1].input(self)

    def update(self):
        if self.stackScene:
            self.stackScene[-1].update(self)

    def draw(self, dt: float):
        if self.stackScene:
            self.stackScene[-1].draw(dt)

    def set(self, scene: Scene):
        self.stackScene = [scene]
