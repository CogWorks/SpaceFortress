import pygame
import random, os
from timer import Timer

from sftoken import Token

import pygl2d

class Bonus(Token):
    """bonus symbol"""
    def __init__(self, app):
        super(Bonus, self).__init__()
        self.position.x = 0
        self.position.y = 0
        self.app = app
        self.symbols = self.app.config['Bonus']['non_bonus_symbols']
        self.set_bonus_location()
        self.visible = False
        self.font = self.app.f28
        self.bonus_symbol = self.app.config['Bonus']['bonus_symbol']
        self.current_symbol = None
        self.prior_symbol = None
        if self.app.config['General']['bonus_system'] == "AX-CPT":
            self.bonus_count = 1
        else:
            self.bonus_count = 0
        self.flag = False
        self.probability = self.app.config['Bonus']['bonus_probability']
        self.timer = Timer(self.app.gametimer.elapsed)
        #new attributes for AX-CPT
        self.cue_time = self.app.config['AX-CPT']['cue_visibility']
        self.target_time = self.app.config['AX-CPT']['target_visibility']
        self.isi_time = self.app.config['AX-CPT']['isi_time']
        self.iti_time = self.app.config['AX-CPT']['iti_time']
        self.state = self.app.config['AX-CPT']['state']
        self.ax_prob = self.app.config['AX-CPT']['ax_prob']
        self.ay_prob = self.app.config['AX-CPT']['ay_prob']
        self.bx_prob = self.app.config['AX-CPT']['bx_prob']
        self.by_prob = self.app.config['AX-CPT']['by_prob']
        self.a_symbols = self.app.config['AX-CPT']['a_symbols']
        self.b_symbols = self.app.config['AX-CPT']['b_symbols']
        self.x_symbols = self.app.config['AX-CPT']['x_symbols']
        self.y_symbols = self.app.config['AX-CPT']['y_symbols']
        self.current_pair = "nothing" #either "ax", "ay", "bx", or "by"
        self.current_symbols = self.pick_next_pair()
        self.axcpt_flag = False #bonus is capturable
        
    def generate_new_position(self):
        self.position.x = random.randint(self.app.world.left + 30, self.app.world.right - 30)
        self.position.y = random.randint(self.app.world.top + 30, self.app.world.bottom - 30)
        
    def set_bonus_location(self):
        if self.app.config['General']['bonus_location'] == 'Random':           
            self.generate_new_position()
            while self.get_distance_to_object(self.app.fortress) < self.app.config['Hexagon']['small_hex'] * self.app.aspect_ratio * 1.25:
                self.generate_new_position()
        elif self.app.config['General']['bonus_location'] == 'Probabilistic':
            w = self.app.world.width / 5
            h = self.app.world.height / 5
            probs = map(float, self.app.config['Bonus']['quadrant_probs'].split(','))
            r
            if r <= probs[0]:
                self.position.x = self.app.world.left + w
                self.position.y = self.app.world.top + h
            elif r <= probs[1]:
                self.position.x = self.app.world.left + w * 4
                self.position.y = self.app.world.top + h
            elif r <= probs[2]:
                self.position.x = self.app.world.left + w
                self.position.y = self.app.world.top + h * 4
            else:
                self.position.x = self.app.world.left + w * 4
                self.position.y = self.app.world.top + h * 4
        else:
            self.position.x = self.app.config['Bonus']['bonus_pos_x'] * self.app.aspect_ratio
            self.position.y = self.app.config['Bonus']['bonus_pos_y'] * self.app.aspect_ratio
        
    def draw(self):
        """draws bonus symbol to screen"""
        bonus = pygl2d.font.RenderText("%s" % self.current_symbol, (255, 200, 0), self.font)
        bonus_rect = bonus.get_rect()
        bonus_rect.center = (self.position.x, self.position.y)
        bonus.draw(bonus_rect.topleft)
    
    def get_new_symbol(self):
        """assigns new bonus symbol"""
        self.prior_symbol = self.current_symbol
        if random.random() < self.probability:
            self.current_symbol = self.bonus_symbol
        else:
            self.current_symbol = random.sample(self.symbols, 1)[0]
            self.flag = True
        self.set_bonus_location()
        self.bonus_count += 1
            
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
            self.app.bonus_captured = False
            self.current_symbols = self.pick_next_pair()
            # idk if this is the best place for this ~rmh
            self.set_bonus_location()
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
            self.prior_symbol = self.current_symbol
        elif self.state == "isi" and self.timer.elapsed() > self.isi_time: #make target appear
            self.bonus_count += 1
            self.timer.reset()
            if self.isi_time == 800:
                self.isi_time = 4000
            else:
                self.isi_time = 800
            self.state = "target"
            self.app.bonus_captured = False
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
            self.prior_symbol = self.current_symbol
            
        
