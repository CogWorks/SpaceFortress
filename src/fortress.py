from __future__ import division
from vector2D import Vector2D
import math, os
import shell
import pygame
import picture
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
  
    def compute(self):
        """determines orientation of fortress"""
        if self.app.ship.alive:
            self.orientation = self.to_target_orientation(self.app.ship) // self.sector_size * self.sector_size #integer division truncates
        if self.orientation != self.last_orientation:
            self.last_orientation = self.orientation
            self.timer.reset()
        if self.timer.elapsed() >= self.lock_time and self.app.ship.alive and self.app.fortress.alive:
            self.app.gameevents.add("fire", "fortress", "ship")
            self.fire()
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
            pygame.draw.circle(worldsurf, (0, 0, 0), (self.position.x, self.position.y), int(30 * self.app.aspect_ratio))
            self.sinphi = math.sin(math.radians((self.orientation) % 360))
            self.cosphi = math.cos(math.radians((self.orientation) % 360))
            x1 = 18 * self.cosphi * self.app.aspect_ratio + self.position.x
            y1 = -(18 * self.sinphi) * self.app.aspect_ratio + self.position.y
            x2 = 36 * self.cosphi * self.app.aspect_ratio + self.position.x
            y2 = -(36 * self.sinphi) * self.app.aspect_ratio + self.position.y
            x3 = (18 * self.cosphi - -18 * self.sinphi) * self.app.aspect_ratio + self.position.x
            y3 = (-(-18 * self.cosphi + 18 * self.sinphi)) * self.app.aspect_ratio + self.position.y
            x4 = -(-18 * self.sinphi) * self.app.aspect_ratio + self.position.x
            y4 = -(-18 * self.cosphi) * self.app.aspect_ratio + self.position.y
            x5 = (18 * self.cosphi - 18 * self.sinphi) * self.app.aspect_ratio + self.position.x
            y5 = (-(18 * self.cosphi + 18 * self.sinphi)) * self.app.aspect_ratio + self.position.y
            x6 = -(18 * self.sinphi) * self.app.aspect_ratio + self.position.x
            y6 = -(18 * self.cosphi) * self.app.aspect_ratio + self.position.y
            pygame.draw.line(worldsurf, (255, 255, 0), (x1, y1), (x2, y2), self.app.linewidth)
            pygame.draw.line(worldsurf, (255, 255, 0), (x3, y3), (x5, y5), self.app.linewidth)
            pygame.draw.line(worldsurf, (255, 255, 0), (x3, y3), (x4, y4), self.app.linewidth)
            pygame.draw.line(worldsurf, (255, 255, 0), (x5, y5), (x6, y6), self.app.linewidth)
        
