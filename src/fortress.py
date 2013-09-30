from __future__ import division
from vector2D import Vector2D
import math, os
import shell
import pygame
from gameevent import GameEvent
from timer import Timer
from sftoken import Token

import pkg_resources

import pygl2d

class Fortress(Token):
    """represents the fortress object that typically appears in the center of the worldsurf"""
    def __init__(self, app):
        super(Fortress, self).__init__()
        self.app = app
        self.position.x = self.app.world.centerx
        self.position.y = self.app.world.centery
        self.color = (255, 255, 0)
        self.collision_radius = self.app.config['Fortress']['fortress_radius'] * self.app.aspect_ratio
        self.last_orientation = self.orientation 
        self.timer = Timer(self.app.gametimer.elapsed)
        self.sector_size = self.app.config['Fortress']['fortress_sector_size']
        self.lock_time = self.app.config['Fortress']['fortress_lock_time']
        self.reset_timer = Timer(self.app.gametimer.elapsed)
        self.alive = True
        if self.app.config['Graphics']['fancy']:
            self.fortress = pygl2d.image.Image(pkg_resources.resource_stream("resources", 'gfx/psf5.png'))
            self.fortress_rect = self.fortress.get_rect()
            self.fortress.scale((72 * self.app.aspect_ratio) / 128)
        else:
            self.calculate_vector_points()
            
    def get_width(self):
        if self.app.config['Graphics']['fancy']:
            return self.fortress_rect.width
        else:
            s = [self.x1,self.x2,self.x3,self.x4,self.x5,self.x5]
            return abs(max(s) - min(s))

    def get_height(self):
        if self.app.config['Graphics']['fancy']:
            return self.fortress_rect.height
        else:
            s = [self.y1,self.y2,self.y3,self.y4,self.y5,self.y6]
            return abs(max(s) - min(s))

    def calculate_vector_points(self):
        sinphi = math.sin(math.radians((self.orientation) % 360))
        cosphi = math.cos(math.radians((self.orientation) % 360))
        self.x1 = 18 * cosphi * self.app.aspect_ratio + self.position.x
        self.y1 = -(18 * sinphi) * self.app.aspect_ratio + self.position.y
        self.x2 = 36 * cosphi * self.app.aspect_ratio + self.position.x
        self.y2 = -(36 * sinphi) * self.app.aspect_ratio + self.position.y
        self.x3 = (18 * cosphi - -18 * sinphi) * self.app.aspect_ratio + self.position.x
        self.y3 = (-(-18 * cosphi + 18 * sinphi)) * self.app.aspect_ratio + self.position.y
        self.x4 = -(-18 * sinphi) * self.app.aspect_ratio + self.position.x
        self.y4 = -(-18 * cosphi) * self.app.aspect_ratio + self.position.y
        self.x5 = (18 * cosphi - 18 * sinphi) * self.app.aspect_ratio + self.position.x
        self.y5 = (-(18 * cosphi + 18 * sinphi)) * self.app.aspect_ratio + self.position.y
        self.x6 = -(18 * sinphi) * self.app.aspect_ratio + self.position.x
        self.y6 = -(18 * cosphi) * self.app.aspect_ratio + self.position.y

    def compute(self):
        """determines orientation of fortress"""
        if self.app.ship.alive:
            self.orientation = self.to_target_orientation(self.app.ship) // self.sector_size * self.sector_size #integer division truncates
        if self.orientation != self.last_orientation:
            self.last_orientation = self.orientation
            self.timer.reset()
        if self.timer.elapsed() >= self.lock_time and self.app.ship.alive and self.app.fortress.alive:
            self.fire()
            self.app.gameevents.add("fire", "fortress", "ship")
            self.timer.reset()
        if not self.alive and self.reset_timer.elapsed() > 1000:
            self.alive = True
            
    def fire(self):
        self.app.snd_shell_fired.play()
        self.app.shell_list.append(shell.Shell(self.app, self.to_target_orientation(self.app.ship)))
        
    def draw(self):
        """draws fortress to worldsurf"""
        if self.app.config['Graphics']['fancy']:
            self.fortress.rotate(self.orientation - 90)
            self.fortress_rect.center = (self.position.x, self.position.y)
            self.fortress.draw(self.fortress_rect.topleft)
        else:
            #pygame.draw.circle(worldsurf, (0, 0, 0), (self.position.x, self.position.y), int(30 * self.app.aspect_ratio))
            self.calculate_vector_points()
            pygl2d.draw.line((self.x1, self.y1), (self.x2, self.y2), self.color, self.app.linewidth)
            pygl2d.draw.line((self.x3, self.y3), (self.x5, self.y5), self.color, self.app.linewidth)
            pygl2d.draw.line((self.x3, self.y3), (self.x4, self.y4), self.color, self.app.linewidth)
            pygl2d.draw.line((self.x5, self.y5), (self.x6, self.y6), self.color, self.app.linewidth)
        
