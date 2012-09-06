#shell.py
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

class Shell(sf_object.object.Object):
    """represents the weapon fired from the fortress"""
    def __init__(self, app, orientation):
        super(Shell, self).__init__()
        self.app = app
        self.orientation = orientation
        self.position.x = 355
        self.position.y = 315
        self.speed = int(app.config["shell_speed"])
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
        
        pygame.draw.line(worldsurf, (255,0,0), (x1, y1), (x2, y2))
        pygame.draw.line(worldsurf, (255,0,0), (x2, y2), (x3, y3))
        pygame.draw.line(worldsurf, (255,0,0), (x3, y3), (x4, y4))
        pygame.draw.line(worldsurf, (255,0,0), (x4, y4), (x1, y1))