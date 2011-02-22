#fortress.py
#this code is to be placed in the "tokens" subfolder
#Space Fortress 5
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2010
from __future__ import division
from vector2D import Vector2D
import math
import token
import shell
import pygame
from gameevent import GameEvent
from timer import Timer as clock_timer
from timer import FrameTimer as frame_timer

class Fortress(token.Token):
    """represents the fortress object that typically appears in the center of the worldsurf"""
    def __init__(self, app):
        super(Fortress, self).__init__()
        self.app = app
        self.position.x = int(app.config["fortress_pos_x"])
        self.position.y = int(app.config["fortress_pos_y"])
        self.collision_radius = int(app.config["fortress_radius"]) 
        self.last_orientation = self.orientation 
        if not self.app.config["human"]:
            self.timer = frame_timer(self.app)
        else:
            self.timer = clock_timer()
        self.sector_size = int(app.config["fortress_sector_size"])
        self.lock_time = int(app.config["fortress_lock_time"])
        self.reset_timer = clock_timer()
        self.alive = True
        
  
    def compute(self):
        """determines orientation of fortress"""
        if self.app.ship.alive:
            self.orientation = self.to_target_orientation(self.app.ship) // self.sector_size * self.sector_size #integer division truncates
        if self.orientation != self.last_orientation:
            self.last_orientation = self.orientation
            self.timer.reset()
        if self.timer.elapsed() >= self.lock_time and self.app.ship.alive and self.app.fortress.alive:
            self.app.gameevents.append(GameEvent("fire", "fortress", "ship"))
            self.fire()
            self.timer.reset()
        if not self.alive and self.reset_timer.elapsed() > 1000:
            self.alive = True
            
    def fire(self):
        self.app.sounds.shell_fired.play()
        self.app.shell_list.append(shell.Shell(self.app, self.to_target_orientation(self.app.ship)))
        
    def draw(self, worldsurf):
        """draws fortress to worldsurf"""
        #draws a small black circle under the fortress so we don't see the shell in the center
        pygame.draw.circle(worldsurf, (0,0,0), (self.position.x, self.position.y), 30)
        #photoshop measurement shows 36 pixels long, and two wings 18 from center and 18 long
        #these formulae rotate about the origin. Need to translate to origin, rotate, and translate back
        self.sinphi = math.sin(math.radians((self.orientation) % 360))
        self.cosphi = math.cos(math.radians((self.orientation) % 360))
        #x1 = self.position.x
        #y1 = self.position.y
        x1 = 18 * self.cosphi + self.position.x
        y1 = -(18 * self.sinphi) + self.position.y
        x2 = 36 * self.cosphi + self.position.x
        y2 = -(36 * self.sinphi) + self.position.y
        #x3, y3 = 18, -18
        x3 = 18 * self.cosphi - -18 * self.sinphi + self.position.x
        y3 = -(-18 * self.cosphi + 18 * self.sinphi) + self.position.y
        #x4, y4 = 0, -18
        x4 = -(-18 * self.sinphi) + self.position.x
        y4 = -(-18 * self.cosphi) + self.position.y
        #x5, y5 = 18, 18
        x5 = 18 * self.cosphi - 18 * self.sinphi + self.position.x
        y5 = -(18 * self.cosphi + 18 * self.sinphi) + self.position.y
        #x6, y6 = 0, 18
        x6 = - (18 * self.sinphi) + self.position.x
        y6 = -(18 * self.cosphi) + self.position.y
        
        pygame.draw.line(worldsurf, (255,255,0), (x1,y1), (x2, y2), self.app.linewidth)
        pygame.draw.line(worldsurf, (255,255,0), (x3,y3), (x5, y5), self.app.linewidth)
        pygame.draw.line(worldsurf, (255,255,0), (x3,y3), (x4, y4), self.app.linewidth)
        pygame.draw.line(worldsurf, (255,255,0), (x5,y5), (x6, y6), self.app.linewidth)
        