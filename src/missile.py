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
        self.dirt = []
        if orientation:
            self.orientation = orientation
        else:
            self.orientation = self.app.ship.orientation
        self.position.x = self.app.ship.position.x
        self.position.y = self.app.ship.position.y
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
        
        
    def draw(self):
        for dirt in self.dirt:
            self.app.screen.blit(self.app.starfield, dirt, dirt)
            self.app.screen_buffer.blit(self.app.starfield, dirt, dirt)        
        if self.app.config['Graphics']['fancy']:
            self.missile.rect.centerx = self.position.x
            self.missile.rect.centery = self.position.y
            self.app.screen_buffer.blit(self.missile.image, self.missile.rect)
            self.dirt = [self.missile.rect]
        else:
            self.sinphi = math.sin(math.radians((self.orientation) % 360))
            self.cosphi = math.cos(math.radians((self.orientation) % 360))
            self.x1 = self.position.x
            self.y1 = self.position.y
            self.x2 = -25 * self.cosphi * self.app.aspect_ratio + self.position.x
            self.y2 = -(-25 * self.sinphi) * self.app.aspect_ratio + self.position.y
            self.x3 = ((-5 * self.cosphi) - (5 * self.sinphi)) * self.app.aspect_ratio + self.position.x
            self.y3 = (-((5 * self.cosphi) + (-5 * self.sinphi))) * self.app.aspect_ratio + self.position.y
            self.x4 = ((-5 * self.cosphi) - (-5 * self.sinphi)) * self.app.aspect_ratio + self.position.x
            self.y4 = (-((-5 * self.cosphi) + (-5 * self.sinphi))) * self.app.aspect_ratio + self.position.y
            self.dirt = [
                         pygame.draw.line(self.app.screen_buffer, (255, 0, 0), (self.x1, self.y1), (self.x2, self.y2), self.app.linewidth),
                         pygame.draw.line(self.app.screen_buffer, (255, 0, 0), (self.x1, self.y1), (self.x3, self.y3), self.app.linewidth),
                         pygame.draw.line(self.app.screen_buffer, (255, 0, 0), (self.x1, self.y1), (self.x4, self.y4), self.app.linewidth)]
        self.app.dirty_rects += self.dirt
        
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
