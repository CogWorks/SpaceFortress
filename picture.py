import pygame
import numpy
from random import randrange

pygame.surfarray.use_arraytype("numpy")

class Picture:
    def __init__(self, filename, scale, rotate=0):
        self.image = pygame.image.load(filename).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (int(self.image.get_width()*scale), int(self.image.get_height()*scale)))
        self.rotate(rotate)
        self.rect = self.image.get_rect()
    
    def rotate(self, rotate):
        self.image = pygame.transform.rotate(self.image, rotate)
        self.rect = self.image.get_rect()
        
    def random_rotate(self):
        self.image = pygame.transform.rotate(self.image, randrange(0,359))
        self.rect = self.image.get_rect()
        
    def adjust_alpha(self, amount, inplace=True):
        if (type(amount) == int and amount == 255):
            return
        if (isinstance(amount, pygame.Surface)):
            amount = pygame.surfarray.pixels_alpha(amount)
        alpha = pygame.surfarray.pixels_alpha(self.image)
        alpha = (alpha*(amount/255.0)).astype("uint8")
        if inplace:
            pygame.surfarray.pixels_alpha(self.image)[:] = alpha
        else:
            newsurf = self.image.copy()
            pygame.surfarray.pixels_alpha(newsurf)[:] = alpha
            return newsurf