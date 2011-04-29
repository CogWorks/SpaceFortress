import pygame

class Picture:
    def __init__(self, filename, scale):
        self.image = pygame.image.load(filename).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (int(self.image.get_width()*scale), int(self.image.get_height()*scale)))
        self.rect = self.image.get_rect()