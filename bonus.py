#bonus.py
#Pygame Space Fortress
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2008
#Class for bonus object, which displays symbols below the fortress
import sf_object
import pygame
import random

class Bonus(object):
    """bonus symbol"""
    def __init__(self):
        super(Bonus, self).__init__()
        self.symbols = ["#", "&", "*", "%", "@"]
        self.x = 355
        self.y = 390
        self.visible = False
        self.font = pygame.font.Font("fonts/freesansbold.ttf", 28)
        self.bonus_symbol = "$"
        self.current_symbol = ''
        self.prior_symbol = ''
        self.flag = True
        self.probability = 0.3
    
        
    def draw(self, worldsurf):
        """draws bonus symbol to screen"""
        worldsurf.blit(self.font.render("%s"%self.current_symbol, 1, (255, 255, 0)), pygame.Rect(self.x, self.y, 150, 30))
    
    def get_new_symbol(self):
        """assigns new bonus symbol"""
        if random.random() < self.probability:
            self.current_symbol = self.bonus_symbol
        else:
            self.current_symbol = random.sample(self.symbols, 1)[0]
            self.flag = True
        