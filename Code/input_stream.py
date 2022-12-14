import pygame


class Keyboard:
    def __init__(self):
        self.currentKeyStates = None
        self.previousKeyStates = None

    def process_input(self):
        self.previousKeyStates = self.currentKeyStates
        self.currentKeyStates = pygame.key.get_pressed()

    def is_key_down(self, key_code):
        if self.currentKeyStates is None or self.previousKeyStates is None:
            return False
        return self.currentKeyStates[key_code]

    def is_key_pressed(self, key_code):
        if self.currentKeyStates is None or self.previousKeyStates is None:
            return False
        return self.currentKeyStates[key_code] and not self.previousKeyStates[key_code]

    def is_key_released(self, key_code):
        if self.currentKeyStates is None or self.previousKeyStates is None:
            return False
        return not self.currentKeyStates[key_code] and self.previousKeyStates[key_code]


class InputStream:
    def __init__(self):
        self.keyboard = Keyboard()

    def process_input(self):
        self.keyboard.process_input()
