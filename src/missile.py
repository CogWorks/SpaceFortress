from __future__ import division
from vector2D import Vector2D
import math, os
import pygame
import picture
from sftoken import Token

import pkg_resources

class Missile(Token):
    """represents the weapon fired by the ship"""
    def __init__(self, app, orientation=None):
        super(Missile, self).__init__()
        self.app = app
        if orientation:
            self.orientation = orientation
        else:
            self.orientation = self.app.ship.orientation
        self.position.x = self.app.ship.nose[0]
        self.position.y = self.app.ship.nose[1]
        self.collision_radius = self.app.config['Missile']['missile_radius'] * self.app.aspect_ratio
        self.speed = self.app.config['Missile']['missile_speed']
        self.velocity.x = math.cos(math.radians((self.orientation) % 360)) * self.speed
        self.velocity.y = -math.sin(math.radians((self.orientation) % 360)) * self.speed
        if self.app.config['Graphics']['fancy']:
            self.missile = picture.Picture(pkg_resources.resource_stream("resources", 'gfx/plasmabluesmall.png'), 25 * self.app.aspect_ratio / 29, self.orientation - 90)
        
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
        self.x2 = -25 * self.cosphi * self.app.aspect_ratio + self.position.x
        self.y2 = -(-25 * self.sinphi) * self.app.aspect_ratio + self.position.y
        #x3, y3 is -5, +5
        self.x3 = ((-5 * self.cosphi) - (5 * self.sinphi)) * self.app.aspect_ratio + self.position.x
        self.y3 = (-((5 * self.cosphi) + (-5 * self.sinphi))) * self.app.aspect_ratio + self.position.y
        #x4, y4 is -5, -5
        self.x4 = ((-5 * self.cosphi) - (-5 * self.sinphi)) * self.app.aspect_ratio + self.position.x
        self.y4 = (-((-5 * self.cosphi) + (-5 * self.sinphi))) * self.app.aspect_ratio + self.position.y
        
        if self.app.config['Graphics']['fancy']:
            self.missile.rect.centerx = self.position.x
            self.missile.rect.centery = self.position.y
            worldsurf.blit(self.missile.image, self.missile.rect)
        else:
            pygame.draw.line(worldsurf, (255, 0, 0), (self.x1, self.y1), (self.x2, self.y2), self.app.linewidth)
            pygame.draw.line(worldsurf, (255, 0, 0), (self.x1, self.y1), (self.x3, self.y3), self.app.linewidth)
            pygame.draw.line(worldsurf, (255, 0, 0), (self.x1, self.y1), (self.x4, self.y4), self.app.linewidth)
        
    def __str__(self):
        return '(%.2f,%.2f,%.2f)' % (self.position.x, self.position.y, self.orientation)
        
class MissileList(list):
    
    def __init__(self, app):
        super(MissileList, self).__init__()
        self.app = app
        
    def __str__(self):
        s = ''
        for i in range(0, len(self)):
            s = '%s,%s' % (s, self[i])
        return '[%s]' % (s[1:])
