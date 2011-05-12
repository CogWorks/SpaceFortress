#token.py
#this code is to be placed in the "tokens" subfolder
#Space Fortress 5
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2010
from __future__ import division
from vector2D import Vector2D
import math

class Token(object):
    """Base class for all visible Space Fortress tokens (objects)"""
    def __init__(self):
        super(Token, self).__init__()
        self.position = Vector2D()
        self.start_position = Vector2D()
        self.last_position = Vector2D()
        self.velocity = Vector2D()
        self.max_velocity = Vector2D()
        self.orientation = 0
        self.collision_radius = 1
        self.start_health = 1
        self.health = 1
        self.operations = {}
        self.invulnerable = False
        self.alive = True
                
    def take_damage(self, value=1):
        """damages object"""
        if self.invulnerable == False and self.alive == True and value > 0:
            self.health -= value
        if self.health <= 0:
            self.alive = False
            self.health = self.start_health
            
    #utility methods
    
    def to_target_orientation(self, target):
        """find the correct orientation to pursue target"""
        dx = target.position.x - self.position.x
        dy = self.position.y - target.position.y
        return (math.degrees(math.atan2(dy,dx))) % 360
            
    def get_distance_to_object(self, target):
        """Finds the distance between self and some target object"""
        distance = (target.position.x - self.position.x)**2
        distance += (target.position.y - self.position.y)**2
        return math.sqrt(distance)
    
    def get_distance_to_point(self, x, y):
        """Finds the distance between self and some point"""
        distance = (x - self.position.x)**2
        distance += (y - self.position.y)**2
        return math.sqrt(distance)
        
    def collide(self, target):
        """returns true if two collision_radii are overlapping, false otherwise"""
        if self.get_distance_to_object(target) <= self.collision_radius + target.collision_radius:
            return True
        else:
            return False
        
    # def check_world_wrap(self, width, height):
    #     """Checks whether the object has exceeded the world boundaries. Returns 1 if wrap or 0 if no wrap"""
    #     wrap = False
    #     if self.position.x > width:
    #         wrap = True
    #         self.position.x -= width
    #     elif self.position.x < 0:
    #         wrap = True
    #         self.position.x += width
    #     if self.position.x > height:
    #         wrap = True
    #         self.position.y -= height
    #     elif self.position.y < 0:
    #         wrap = True
    #         self.position.y += height    
    #     return wrap
    def out_of_bounds(self, width, height):
        """check if token is outside world boundaries"""
        if self.position.x < 0 or self.position.x > width or self.position.y < 0 or self.position.y > height:
            return True
        else:
            return False
        
    def FSin(self, value):
        """takes angle in degrees and returns sin in radians"""
        return math.sin(value * 0.0174527)  #PI/180
        
      
    def FCos(self, value):
        """takes angle in degrees and returns cos in radians"""
        return math.cos(value * 0.0174527)
        
            
        