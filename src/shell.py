from __future__ import division
from vector2D import Vector2D
import math, os
from sftoken import Token

import pkg_resources

import pygl2d

class Shell(Token):
    """represents the weapon fired from the fortress"""
    def __init__(self, app, orientation):
        super(Shell, self).__init__()
        self.app = app
        self.orientation = orientation
        self.position.x = self.app.fortress.position.x
        self.position.y = self.app.fortress.position.y
        self.color = (255, 0, 0)
        self.speed = self.app.config['Shell']['shell_speed']
        self.collision_radius = 3 * self.app.aspect_ratio
        self.velocity.x = math.cos(math.radians((self.orientation) % 360)) * self.speed
        self.velocity.y = -math.sin(math.radians((self.orientation) % 360)) * self.speed
        if self.app.config['Graphics']['fancy']:
            self.shell = pygl2d.image.Image(pkg_resources.resource_stream("resources", 'gfx/plasmaredbig.png'))
            self.shell_rect = self.shell.get_rect()
            self.shell.scale(24 * self.app.aspect_ratio / 43)
            self.shell.rotate(self.orientation - 90)
        
    def compute(self):
        """calculates new position of shell"""
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y
               
    def draw(self):
        """draws shell to worldsurf"""       
        if self.app.config['Graphics']['fancy']:
            self.shell_rect.center = (self.position.x, self.position.y)
            self.shell.draw(self.shell_rect.topleft)
        else:
            self.sinphi = math.sin(math.radians((self.orientation) % 360))
            self.cosphi = math.cos(math.radians((self.orientation) % 360))
            x1 = -8 * self.cosphi * self.app.aspect_ratio + self.position.x
            y1 = -(-8 * self.sinphi) * self.app.aspect_ratio + self.position.y
            x2 = -(-6 * self.sinphi) * self.app.aspect_ratio + self.position.x
            y2 = -(-6 * self.cosphi) * self.app.aspect_ratio + self.position.y
            x3 = 16 * self.cosphi * self.app.aspect_ratio + self.position.x
            y3 = -(16 * self.sinphi) * self.app.aspect_ratio + self.position.y
            x4 = -(6 * self.sinphi) * self.app.aspect_ratio + self.position.x
            y4 = -(6 * self.cosphi) * self.app.aspect_ratio + self.position.y
            pygl2d.draw.line((x1, y1), (x2, y2), self.color, self.app.linewidth)
            pygl2d.draw.line((x2, y2), (x3, y3), self.color, self.app.linewidth)
            pygl2d.draw.line((x3, y3), (x4, y4), self.color, self.app.linewidth)
            pygl2d.draw.line((x4, y4), (x1, y1), self.color, self.app.linewidth)
        
    def __str__(self):
        return '(%.2f,%.2f,%.2f)' % (self.position.x, self.position.y, self.orientation)
    
class ShellList(list):
    
    def __init__(self, app):
        super(ShellList, self).__init__()
        self.app = app
        
    def __str__(self):
        s = ''
        for i in range(0, len(self)):
            s = '%s,%s' % (s, self[i])
        return '[%s]' % (s[1:])
