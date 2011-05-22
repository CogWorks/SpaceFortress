import pygame

class Picture:
    def __init__(self, filename, scale, rotate=0):
        self.image = pygame.image.load(filename).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (int(self.image.get_width()*scale), int(self.image.get_height()*scale)))
        self.image = pygame.transform.rotate(self.image, rotate)
        self.rect = self.image.get_rect()