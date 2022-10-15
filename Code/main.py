import pygame
from settings import load_settings
import ctypes
from scene import SceneManager

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
        self.sceneManager = SceneManager(self.gameCanvas)

    def render(self):
        self.display.blit(self.gameCanvas, (0, 0))

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                exit()

            self.sceneManager.event_loop(event)

    def run(self):
        while self.running:
            self.event_loop()
            self.sceneManager.render(self.clock.tick() / 1000)
            self.render()
            pygame.display.update()


if __name__ == '__main__':
    Game().run()
