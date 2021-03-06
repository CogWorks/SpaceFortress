from __future__ import division
from vector2D import Vector2D
import math, os
import pygame
from sftoken import Token

import pkg_resources

import pygl2d

class Missile(Token):
    """represents the weapon fired by the ship"""
    def __init__(self, app, orientation=None):
        super(Missile, self).__init__()
        self.app = app
        if orientation:
            self.orientation = orientation
        else:
            self.orientation = self.app.ship.orientation
        self.color = (255, 0, 0)
        self.position.x = self.app.ship.position.x
        self.position.y = self.app.ship.position.y
        self.collision_radius = self.app.config['Missile']['missile_radius'] * self.app.aspect_ratio
        self.speed = self.app.config['Missile']['missile_speed']
        self.velocity.x = math.cos(math.radians((self.orientation) % 360)) * self.speed
        self.velocity.y = -math.sin(math.radians((self.orientation) % 360)) * self.speed
        if self.app.config['Graphics']['fancy']:
            self.missile = pygl2d.image.Image(pkg_resources.resource_stream("resources", 'gfx/plasmabluesmall.png'))
            self.missile_rect = self.missile.get_rect()
            self.missile.scale(25 * self.app.aspect_ratio / 29)
            self.missile.rotate(self.orientation - 90)
        
    def compute(self):
        """calculates new position of ship's missile"""
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y
        
        
    def draw(self):
        """draws ship's missile to worldsurf"""
        if self.app.config['Graphics']['fancy']:
            self.missile_rect.center = (self.position.x, self.position.y)
            self.missile.draw(self.missile_rect.topleft)
        else:
            sinphi = math.sin(math.radians((self.orientation) % 360))
            cosphi = math.cos(math.radians((self.orientation) % 360))
            x1 = self.position.x
            y1 = self.position.y
            x2 = -25 * cosphi * self.app.aspect_ratio + self.position.x
            y2 = -(-25 * sinphi) * self.app.aspect_ratio + self.position.y
            x3 = ((-5 * cosphi) - (5 * sinphi)) * self.app.aspect_ratio + self.position.x
            y3 = (-((5 * cosphi) + (-5 * sinphi))) * self.app.aspect_ratio + self.position.y
            x4 = ((-5 * cosphi) - (-5 * sinphi)) * self.app.aspect_ratio + self.position.x
            y4 = (-((-5 * cosphi) + (-5 * sinphi))) * self.app.aspect_ratio + self.position.y
            pygl2d.draw.line((x1, y1), (x2, y2), self.color, self.app.linewidth)
            pygl2d.draw.line((x1, y1), (x3, y3), self.color, self.app.linewidth)
            pygl2d.draw.line((x1, y1), (x4, y4), self.color, self.app.linewidth)
        
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
