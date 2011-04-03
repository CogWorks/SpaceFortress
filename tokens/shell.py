#shell.py
#this code is to be placed in the "tokens" subfolder
#Space Fortress 5
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2010
from __future__ import division
from vector2D import Vector2D
import math
import token
import pygame
#from frame import Frame

class Shell(token.Token):
    """represents the weapon fired from the fortress"""
    def __init__(self, app, orientation):
        super(Shell, self).__init__()
        self.app = app
        self.orientation = orientation
        self.position.x = self.app.fortress.position.x
        self.position.y = self.app.fortress.position.y
        self.speed = self.app.config.get_setting('Shell','shell_speed')
        self.collision_radius = 3
        self.velocity.x = math.cos(math.radians((self.orientation) % 360)) * self.speed
        self.velocity.y = -math.sin(math.radians((self.orientation) % 360)) * self.speed
        
    def compute(self):
        """calculates new position of shell"""
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y
               
    def draw(self, worldsurf):
        """draws shell to worldsurf"""       
        #photoshop measurement shows, from center, 16 points ahead, 8 points behind, and 6 points to either side
        #NewX = (OldX*Cos(Theta)) - (OldY*Sin(Theta))
        #NewY = -((OldY*Cos(Theta)) + (OldX*Sin(Theta))) flip 'cause +y is down
        #these formulae rotate about the origin. Need to translate to origin, rotate, and translate back
        self.sinphi = math.sin(math.radians((self.orientation) % 360))
        self.cosphi = math.cos(math.radians((self.orientation) % 360))
        
        x1 = -8 * self.cosphi + self.position.x
        y1 = -(-8 * self.sinphi) + self.position.y
        x2 = -(-6 * self.sinphi) + self.position.x
        y2 = -(-6 * self.cosphi) + self.position.y
        x3 = 16 * self.cosphi + self.position.x
        y3 = -(16 * self.sinphi) + self.position.y
        x4 = -(6 * self.sinphi) + self.position.x
        y4 = -(6 * self.cosphi) + self.position.y
        
        pygame.draw.line(worldsurf, (255,0,0), (x1, y1), (x2, y2), self.app.linewidth)
        pygame.draw.line(worldsurf, (255,0,0), (x2, y2), (x3, y3), self.app.linewidth)
        pygame.draw.line(worldsurf, (255,0,0), (x3, y3), (x4, y4), self.app.linewidth)
        pygame.draw.line(worldsurf, (255,0,0), (x4, y4), (x1, y1), self.app.linewidth)