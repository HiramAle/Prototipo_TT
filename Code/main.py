import pygame
from settings import load_settings
import ctypes
from scene import SceneManager, MainScene

# import test

# Avoid DPI virtualization
ctypes.windll.user32.SetProcessDPIAware()


class Game:
    def __init__(self):
        pygame.init()
        self.settings = load_settings()
        self.width = self.settings.getint("display", "width")
        self.height = self.settings.getint("display", "height")
        self.display = pygame.display.set_mode((self.width, self.height))
        self.gameCanvas = pygame.Surface((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.running = True
        # self.sceneManager = test.SceneManager()
        # self.sceneManager.enter_scene(test.MainMenu(self.gameCanvas))
        self.sceneManager = SceneManager(self.display)
        self.sceneManager.enter_scene("main_menu")

    def render(self):
        self.display.blit(self.gameCanvas, (0, 0))

    def event_loop(self):
        # self.sceneManager.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                exit()

            self.sceneManager.event_loop(event)

            # if event.type == pygame.KEYDOWN:
            #   self.sceneManager.input()

    def run(self):
        while self.running:
            # print([i.__class__.__name__ for i in self.sceneManager.stackScene])
            self.event_loop()
            # self.sceneManager.draw(self.clock.tick() / 1000)
            self.sceneManager.render(self.clock.tick() / 1000)
            self.render()
            print(self.sceneManager.sceneStack)
            pygame.display.update()


if __name__ == '__main__':
    Game().run()
