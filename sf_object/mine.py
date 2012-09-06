#mine.py
#this code is to be placed in the "sf_object" subfolder
#Pygame Space Fortress
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2008
from __future__ import division
from Vector2D import Vector2D
import math
import sf_object
import string
import random
import pygame
#from frame import Frame

class Mine(sf_object.object.Object):
    """represents the friend or foe mine object"""
    def __init__(self, app):
        super(Mine, self).__init__()
        self.position.x = 600
        self.position.y = 400
        self.app = app
        self.speed = 10
        self.health = 1
        self.timeout = 15000 #milliseconds after destruction when mine "gives up"
        self.reset_time = 5000 #milliseconds after destruction when mine "respawns"
        self.alive = False
        self.collision_radius = 20
        self.foe_probability = 0.3
        self.life_span = 160
        self.sleep_span = 200
        self.minimum_spawn_distance = 320
        self.maximum_spawn_distance = 640
        self.iff_lower_bound = 100
        self.iff_upper_bound = 300
        self.speed = 2
        self.num_foes = 3
        self.letters = list(string.letters[26:]) #list of uppercase letters
        self.letters.remove("T") #Screws up Lisp's read-from-string
        self.exists = True
    
    def generate_foes(self, num):
        """determine which mine designations are 'foes'"""
        self.foe_letters = random.sample(self.letters, num)
        self.foe_letters.sort()
        for each in self.foe_letters:
            self.letters.remove(each)
            
    def generate_new_position(self):
        """chooses random location to place mine"""
        self.position.x = random.random() * (self.app.WORLD_WIDTH - 40) + 20
        self.position.y = random.random() * (self.app.WORLD_HEIGHT - 40) + 20
            
    def reset(self):
        """resets mine - makes alive, places it a distance away from the ship, gets IFF tag"""
        self.alive = True
        if random.random() < self.foe_probability:
            self.app.score.iff = random.sample(self.foe_letters, 1)[0]
        else:
            self.app.score.iff = random.sample(self.letters, 1)[0]
        self.generate_new_position()
        while self.get_distance_to_object(self.app.ship) < 400:
            self.generate_new_position()
        
    def compute(self):
        """calculates new position of mine"""
        self.velocity.x = math.cos(math.radians((self.to_target_orientation(self.app.ship)) % 360)) * self.speed
        self.velocity.y = -math.sin(math.radians((self.to_target_orientation(self.app.ship)) % 360)) * self.speed
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y
        
    def draw(self, worldsurf):
        """draws mine to worldsurf"""
        pygame.draw.line(worldsurf, (0,255,255), (self.position.x - 16, self.position.y), (self.position.x, self.position.y - 24))
        pygame.draw.line(worldsurf, (0,255,255), (self.position.x, self.position.y - 24), (self.position.x + 16, self.position.y))
        pygame.draw.line(worldsurf, (0,255,255), (self.position.x + 16, self.position.y), (self.position.x, self.position.y + 24))
        pygame.draw.line(worldsurf, (0,255,255), (self.position.x, self.position.y + 24), (self.position.x - 16, self.position.y))