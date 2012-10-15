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

class Fortress(Token):
    """represents the fortress object that typically appears in the center of the worldsurf"""
    def __init__(self, app):
        super(Fortress, self).__init__()
        self.app = app
        self.dirt = []
        self.position.x = int(self.app.config['Fortress']['fortress_pos_x'] * self.app.aspect_ratio)
        self.position.y = int(self.app.config['Fortress']['fortress_pos_y'] * self.app.aspect_ratio)
        self.collision_radius = self.app.config['Fortress']['fortress_radius'] * self.app.aspect_ratio
        self.last_orientation = self.orientation 
        self.timer = Timer(self.app.gametimer.elapsed)
        self.sector_size = self.app.config['Fortress']['fortress_sector_size']
        self.lock_time = self.app.config['Fortress']['fortress_lock_time']
        self.reset_timer = Timer(self.app.gametimer.elapsed)
        self.alive = True
        if self.app.config['Graphics']['fancy']:
            self.fortress = picture.Picture(pkg_resources.resource_stream("resources", 'gfx/psf5.png'), (72 * self.app.aspect_ratio) / 128)
        
  
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
        for dirt in self.dirt:
            self.app.screen.blit(self.app.starfield, dirt, dirt)
            self.app.screen_buffer.blit(self.app.starfield, dirt, dirt)
        if self.app.config['Graphics']['fancy']:
            fortress = pygame.transform.rotate(self.fortress.image, self.orientation - 90)
            fortressrect = fortress.get_rect()
            fortressrect.centerx = self.position.x
            fortressrect.centery = self.position.y
            self.app.screen_buffer.blit(fortress, fortressrect)
            self.dirt = [fortressrect]
        else:
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
            self.dirt = [
                 pygame.draw.line(self.app.screen_buffer, (255, 255, 0), (x1, y1), (x2, y2), self.app.linewidth),
                 pygame.draw.line(self.app.screen_buffer, (255, 255, 0), (x3, y3), (x5, y5), self.app.linewidth),
                 pygame.draw.line(self.app.screen_buffer, (255, 255, 0), (x3, y3), (x4, y4), self.app.linewidth),
                 pygame.draw.line(self.app.screen_buffer, (255, 255, 0), (x5, y5), (x6, y6), self.app.linewidth)]
        self.app.dirty_rects += self.dirt
        
