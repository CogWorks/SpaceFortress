from __future__ import division
from vector2D import Vector2D
import math

class Token(object):
    """Base class for all visible Space Fortress tokens (objects)"""
    def __init__(self):
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
        return (math.degrees(math.atan2(dy, dx))) % 360
            
    def get_distance_to_object(self, target):
        """Finds the distance between self and some target object"""
        distance = (target.position.x - self.position.x) ** 2
        distance += (target.position.y - self.position.y) ** 2
        return math.sqrt(distance)
    
    def get_distance_to_point(self, x, y):
        """Finds the distance between self and some point"""
        distance = (x - self.position.x) ** 2
        distance += (y - self.position.y) ** 2
        return math.sqrt(distance)
        
    def collide(self, target):
        """returns true if two collision_radii are overlapping, false otherwise"""
        if self.get_distance_to_object(target) <= self.collision_radius + target.collision_radius:
            return True
        else:
            return False
        
    def out_of_bounds(self, rect):
        """check if token is outside world boundaries"""
        if self.position.x < rect.left or self.position.x > rect.right or self.position.y < rect.top or self.position.y > rect.bottom:
            return True
        else:
            return False        
            
        
