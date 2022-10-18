import pygame
from player import Player


class Overlay:
    def __init__(self, player: Player, display_surface: pygame.Surface):
        self.gameCanvas = display_surface
        self.player = player
        self.font = pygame.font.Font("../Assets/Fonts/monogram.ttf", 40)
        # Overlay
        self.overlayUI = pygame.image.load("../Assets/Overlay/overlay.png").convert_alpha()
        self.overlayUIRect = self.overlayUI.get_rect(topleft=(10, 10))

        self.playerIcon = pygame.image.load("../Assets/Overlay/player_icon.png").convert_alpha()
        self.playerIconRect = self.overlayUI.get_rect(topleft=(14, 9))

    def display(self):
        money = self.player.itemInventory["money"]
        money_surf = self.font.render(str(money), False, "#E2E2E2")
        self.gameCanvas.blit(self.overlayUI, self.overlayUIRect)
        self.gameCanvas.blit(self.playerIcon, self.playerIconRect)
        self.gameCanvas.blit(money_surf, (180, 63))
