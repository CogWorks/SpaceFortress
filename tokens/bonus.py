#bonus.py
#Space Fortress 5
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2010
#Class for bonus object, which displays symbols below the fortress
import pygame
import random
from timer import Timer

class Bonus(object):
    """bonus symbol"""
    def __init__(self, app):
        super(Bonus, self).__init__()
        self.app = app
        self.symbols = app.config["non_bonus_symbols"]
        if not app.config["randomize_bonus_pos"]:
            self.x = int(app.config["bonus_pos_x"])
            self.y = int(app.config["bonus_pos_y"])
        else:
            self.x = random.randint(20, app.WORLD_WIDTH - 10)
            self.y = random.randint(20, app.WORLD_HEIGHT - 20)
        self.visible = False
        self.font = pygame.font.Font("fonts/freesansbold.ttf", 28)
        self.bonus_symbol = app.config["bonus_symbol"]
        self.current_symbol = None
        self.prior_symbol = None
        self.flag = False
        self.probability = float(app.config["bonus_probability"])
        self.timer = Timer()
        
    def draw(self, worldsurf):
        """draws bonus symbol to screen"""
        worldsurf.blit(self.font.render("%s"%self.current_symbol, 1, (255, 255, 0)), pygame.Rect(self.x, self.y, 150, 30))
    
    def get_new_symbol(self):
        """assigns new bonus symbol"""
        self.prior_symbol = self.current_symbol
        if random.random() < self.probability:
            self.current_symbol = self.bonus_symbol
        else:
            self.current_symbol = random.sample(self.symbols, 1)[0]
            self.flag = True
        if self.app.config["randomize_bonus_pos"]:
            self.x = random.randint(30, self.app.WORLD_WIDTH - 30)
            self.y = random.randint(30, self.app.WORLD_HEIGHT - 30)
            
        