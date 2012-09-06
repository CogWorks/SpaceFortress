#object.py
#this code is to be placed in the "sf_object" subfolder
#Pygame Space Fortress
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2008
from __future__ import division
from Vector2D import Vector2D
import math
#from frame import Frame

class Object(object):
    """Base class for all visible Space Fortress objects"""
    def __init__(self):
        super(Object, self).__init__()
        self.start_position = Vector2D()
        self.position = Vector2D()
        self.last_position = Vector2D()
        self.start_velocity = Vector2D()
        self.velocity = Vector2D()
        self.max_velocity = Vector2D()
        self.start_orientation = 0
        self.orientation = 0
        self.update_delay = 0
        self.velocity_ratio = 1.0
        self.half_size = 0
        self.collision_radius = 1
        self.primary_ID = ""
        self.secondary_ID = ""
        self.hostiles = ""
        self.neutrals = ""
        self.health = 1
        self.damage = 0
        self.operations = {}
        self.invulnerable = False
        self.alive = True
        self.last_born = 0
        self.last_damaged = 0
        self.last_updated = -1
        self.last_died = 0
        self.enable_position_change = True
        self.enable_velocity_change = True
        self.enable_orientation_change = True
        self.enable_tactical_change = True
        self.enable_invulnerability_change = True
        self.all_selections = {}
        
    #state change methods
    
    def update(self, time):
        """updates the current state of the generic object. Should be called once per frame"""
        if self.alive == False:
            return
        self.last_position = self.position
        self.position = Vector2D(self.position.x + self.velocity.y * time, self.position.y + self.velocity.y * time)
        self.last_updated = GameFrame.clock.get_ticks()
        
    def take_damage(self, value=1):
        """damages object"""
        if value>0:
            self.damage += value
        if self.damage >= self.health:
            self.alive = False
            self.damage = 0
            
    #utility methods
    
    def to_target_orientation(self, target):
        """find the correct orientation to pursue target"""
        dx = target.position.x - self.position.x
        dy = self.position.y - target.position.y
        return (math.degrees(math.atan2(dy,dx))) % 360
            
    def get_distance_to_object(self, target):
        """Finds the distance between to a target object"""
        distance = (target.position.x - self.position.x)**2
        distance += (target.position.y - self.position.y)**2
        return math.sqrt(distance)
        
    def test_collision(self, target):
        """returns true if two collision_radii are overlapping, false otherwise"""
        if self.get_distance_to_object(target) <= self.collision_radius + target.collision_radius:
            return True
        else:
            return False
        
    def check_world_wrap(self):
        """Checks whether the object has exceeded the world boundaries. Returns 1 if wrap or 0 if no wrap"""
        wrap = False
        if self.position.x > GameFrame.SCREEN_WIDTH:
            wrap = True
            self.position.x -= GameFrame.SCREEN_WIDTH
        elif self.position.x < 0:
            wrap = True
            self.position.x += GameFrame.SCREEN_WIDTH
        if self.position.x > GameFrame.SCREEN_HEIGHT:
            wrap = True
            self.position.y -= GameFrame.SCREEN_HEIGHT
        elif self.position.y < 0:
            wrap = True
            self.position.y += GameFrame.SCREEN_HEIGHT
            
        return wrap
        
    def FSin(self, value):
        """takes angle in degrees and returns sin in radians"""
        return math.sin(value * 0.0174527)  #PI/180
        
      
    def FCos(self, value):
        """takes angle in degrees and returns cos in radians"""
        return math.cos(value * 0.0174527)
        
            
        