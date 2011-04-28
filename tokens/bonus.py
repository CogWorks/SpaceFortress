#bonus.py
#Space Fortress 5
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2010
#Class for bonus object, which displays symbols below the fortress
import pygame
import random, os
from timer import Timer

class Bonus(object):
    """bonus symbol"""
    def __init__(self, app):
        super(Bonus, self).__init__()
        self.app = app
        self.symbols = self.app.config.get_setting('Bonus','non_bonus_symbols')
        if not self.app.config.get_setting('Bonus','randomize_bonus_pos'):
            self.x = self.app.config.get_setting('Bonus','bonus_pos_x')
            self.y = self.app.config.get_setting('Bonus','bonus_pos_y')
        else:
            self.x = random.randint(20, app.WORLD_WIDTH - 10)
            self.y = random.randint(20, app.WORLD_HEIGHT - 20)
        self.visible = False
        self.font = pygame.font.Font(self.app.fp, int(28*self.app.aspect_ratio))
        self.bonus_symbol = self.app.config.get_setting('Bonus','bonus_symbol')
        self.current_symbol = None
        self.prior_symbol = None
        self.flag = False
        self.probability = self.app.config.get_setting('Bonus','bonus_probability')
        self.timer = Timer()
        #new attributes for AX-CPT
        self.cue_time = self.app.config.get_setting('AX-CPT','cue_visibility')
        self.target_time = self.app.config.get_setting('AX-CPT','target_visibility')
        self.isi_time = self.app.config.get_setting('AX-CPT','isi_time')
        self.iti_time = self.app.config.get_setting('AX-CPT','iti_time')
        self.state = self.app.config.get_setting('AX-CPT','state')
        self.ax_prob = self.app.config.get_setting('AX-CPT','ax_prob')
        self.ay_prob = self.app.config.get_setting('AX-CPT','ay_prob')
        self.bx_prob = self.app.config.get_setting('AX-CPT','bx_prob')
        self.by_prob = self.app.config.get_setting('AX-CPT','by_prob')
        self.a_symbols = self.app.config.get_setting('AX-CPT','a_symbols')
        self.b_symbols = self.app.config.get_setting('AX-CPT','b_symbols')
        self.x_symbols = self.app.config.get_setting('AX-CPT','x_symbols')
        self.y_symbols = self.app.config.get_setting('AX-CPT','y_symbols')
        self.current_pair = "nothing" #either "ax", "ay", "bx", or "by"
        self.current_symbols = self.pick_next_pair()
        self.axcpt_flag = False #bonus is capturable        
        
    def draw(self, worldsurf):
        """draws bonus symbol to screen"""
        worldsurf.blit(self.font.render("%s"%self.current_symbol, 1, (255, 255, 0)), pygame.Rect(self.x*self.app.aspect_ratio, self.y*self.app.aspect_ratio, 150*self.app.aspect_ratio, 30*self.app.aspect_ratio))
    
    def get_new_symbol(self):
        """assigns new bonus symbol"""
        self.prior_symbol = self.current_symbol
        if random.random() < self.probability:
            self.current_symbol = self.bonus_symbol
        else:
            self.current_symbol = random.sample(self.symbols, 1)[0]
            self.flag = True
        if self.app.config.get_setting('Bonus','randomize_bonus_pos'):
            self.x = random.randint(30, self.app.WORLD_WIDTH - 30)
            self.y = random.randint(30, self.app.WORLD_HEIGHT - 30)
            
    def pick_next_pair(self):
        """picks next cue and target for ax-cpt task"""
        chance = random.random()
        if chance < self.ax_prob:
            self.current_pair = "ax"
            return([random.choice(self.a_symbols), random.choice(self.x_symbols)])
        elif chance < (self.ax_prob + self.ay_prob):
            self.current_pair = "ay"
            return([random.choice(self.a_symbols), random.choice(self.y_symbols)])
        elif chance < (self.ax_prob + self.ay_prob + self.bx_prob):
            self.current_pair = "bx"
            return([random.choice(self.b_symbols), random.choice(self.x_symbols)])
        else: 
            self.current_pair = "by"
            return([random.choice(self.b_symbols), random.choice(self.y_symbols)])
            
    def axcpt_update(self):
        """check what to do with ax-cpt task based on state and timer"""
        if self.state == "iti" and self.timer.elapsed() > self.iti_time: #time for a new pair, make cue visible
            self.timer.reset()
            self.state = "cue"
            self.current_symbols = self.pick_next_pair()
            self.axcpt_flag = True
            self.current_symbol = self.current_symbols[0]
            self.visible = True
            if self.current_symbol in self.a_symbols:
                self.app.gameevents.add("bonus", "cue_appears", "correct")
            else:
                self.app.gameevents.add("bonus", "cue_appears", "incorrect")
        elif self.state == "cue" and self.timer.elapsed() > self.cue_time: #make cue disappear
            self.timer.reset()
            self.state = "isi"
            self.visible = False
            self.app.gameevents.add("bonus", "cue_disappears")
        elif self.state == "isi" and self.timer.elapsed() > self.isi_time: #make target appear
            self.timer.reset()
            if self.isi_time == 800:
                self.isi_time = 4000
            else:
                self.isi_time = 800
            self.state = "target"
            self.current_symbol = self.current_symbols[1]
            self.visible = True
            if self.current_symbol in self.x_symbols:
                self.app.gameevents.add("bonus", "target_appears", "correct")
            else:
                self.app.gameevents.add("bonus", "target_appears", "incorrect")
            if self.current_pair == "ax":
                self.app.gameevents.add("bonus_available")
        elif self.state == "target" and self.timer.elapsed() > self.target_time: #make target disappear
            self.timer.reset()
            self.state = "iti"
            self.visible = False
            self.app.gameevents.add("bonus", "target_disappears")
            
        