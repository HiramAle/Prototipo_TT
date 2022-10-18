import pygame
import json


class Button(pygame.sprite.Sprite):
    def __init__(self, position: tuple, text: str, color: str, *groups: pygame.sprite.Group):
        super().__init__(*groups)
        self.data = {}
        self.load_data()
        self.color = color
        self.position = position
        self.text = text
        self.pressed = False
        self.action = False
        self.frames = self.import_assets()
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=self.position)
        self.font = pygame.font.Font("../Assets/Fonts/monogram.ttf", 50)
        self.text_surface = self.font.render(self.text, False, "#f5ffe8")
        self.text_rect = self.text_surface.get_rect(
            center=(self.image.get_width() / 2, self.image.get_height() / 2 - 8))

    def load_data(self):
        with open("../Data/Buttons/buttons.json", "r") as data:
            self.data = json.load(data)

    def import_assets(self):
        image = pygame.image.load(self.data["sprite_sheet_path"]).convert_alpha()
        tile_num_x = image.get_size()[0] // self.data["width"]
        tile_num_y = image.get_size()[1] // self.data["height"]
        cut_images = []
        index_color = self.data["colors"].index(self.color)
        for row in range(tile_num_y):
            if row == index_color:
                for col in range(tile_num_x):
                    x = col * self.data["width"]
                    y = row * self.data["height"]
                    cut = pygame.Surface((self.data["width"], self.data["height"]))
                    cut.set_colorkey(0)
                    cut = cut.convert_alpha()
                    cut.blit(image, (0, 0), pygame.Rect(x, y, self.data["width"], self.data["height"]))
                    cut_images.append(cut)
        return cut_images

    def hover(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            return True
        else:
            return False

    def update(self, dt):
        self.check_click()
        if self.pressed:
            self.text_rect.centery = self.image.get_height() / 2 - 8 + 4
        else:
            self.text_rect.centery = self.image.get_height() / 2 - 8
        self.image.blit(self.text_surface, self.text_rect)

    def check_click(self):
        if self.hover():
            self.image = self.frames[1]
            if pygame.mouse.get_pressed()[0]:
                self.pressed = True
                self.image = self.frames[3]
            else:
                self.pressed = False
        else:
            self.image = self.frames[0]
