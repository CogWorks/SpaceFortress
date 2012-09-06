#missile.py
#this code is to be placed in the "sf_object" subfolder
#Pygame Space Fortress
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2008
from __future__ import division
from Vector2D import Vector2D
import math
import sf_object
import pygame
#from frame import Frame

class Missile(sf_object.object.Object):
    """represents the weapon fired by the ship"""
    def __init__(self, app):
        super(Missile, self).__init__()
        self.app = app
        self.orientation = self.app.ship.orientation
        self.position.x = self.app.ship.position.x
        self.position.y = self.app.ship.position.y
        self.collision_radius = 5
        self.speed = int(app.config["missile_speed"])
        self.velocity.x = math.cos(math.radians((self.orientation) % 360)) * self.speed
        self.velocity.y = -math.sin(math.radians((self.orientation) % 360)) * self.speed
        
    def compute(self):
        """calculates new position of ship's missile"""
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y
        
        
    def draw(self, worldsurf):
        """draws ship's missile to worldsurf"""
        #photoshop measurement shows 25 pixels long, and two wings at 45 degrees to the left and right, 7 pixels long
        #these formulae rotate about the origin. Need to translate to origin, rotate, and translate back
        self.sinphi = math.sin(math.radians((self.orientation) % 360))
        self.cosphi = math.cos(math.radians((self.orientation) % 360))
        self.x1 = self.position.x
        self.y1 = self.position.y
        #x2 is -25
        self.x2 = -25 * self.cosphi + self.position.x
        self.y2 = -(-25 * self.sinphi) + self.position.y
        #x3, y3 is -5, +5
        self.x3 = (-5 * self.cosphi) - (5 * self.sinphi) + self.position.x
        self.y3 = -((5 * self.cosphi) + (-5 * self.sinphi)) + self.position.y
        #x4, y4 is -5, -5
        self.x4 = (-5 * self.cosphi) - (-5 * self.sinphi) + self.position.x
        self.y4 = -((-5 * self.cosphi) + (-5 * self.sinphi)) + self.position.y
        
        pygame.draw.line(worldsurf, (255,0,0), (self.x1, self.y1), (self.x2, self.y2))
        pygame.draw.line(worldsurf, (255,0,0), (self.x1, self.y1), (self.x3, self.y3))
        pygame.draw.line(worldsurf, (255,0,0), (self.x1, self.y1), (self.x4, self.y4))
        
    def collides_with(self, sf_object):
        """determines if mine is colliding with a particular object"""
        incx = math.cos(math.radians((self.orientation) % 360)) # "incremental x" - how much it moves with speed = 1
        incy = -math.sin(math.radians((self.orientation) % 360)) # "incremental y" - how much it moves with speed = 1
        for i in range(1, self.speed + 1):
            tempx = self.position.x + incx * i #test position
            tempy = self.position.y + incy * i
            tempdist = math.sqrt(((tempx - sf_object.position.x) ** 2) + ((tempy - sf_object.position.y) ** 2))
            if tempdist <= self.collision_radius + sf_object.collision_radius:
                return 1
        return 0

