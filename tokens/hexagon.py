#hexagon.py
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

class Hex(token.Token):
    """represents the hexagons the delineate the 'proper' playing space"""
    def __init__(self, app, radius):
        super(Hex, self).__init__()
        self.app = app
        self.original_radius = radius
        self.radius = radius*self.app.aspect_ratio
        self.x = self.app.config.get_setting('Hexagon','hex_pos_x')*self.app.aspect_ratio
        self.y = self.app.config.get_setting('Hexagon','hex_pos_y')*self.app.aspect_ratio
        self.shrink_radius = self.app.config.get_setting('Hexagon','hex_shrink_radius')
        self.set_points(self.radius)
        self.small_hex_flag = False #simple flag to prevent ship getting "stuck" in small hex
        self.color = (0,255,0)
        
    def set_points(self, radius):
        """sets points of hex based on radius"""
        self.PointX1 = (int) (self.x - self.radius)
        self.PointX2 = (int) (self.x - self.radius * 0.5)
        self.PointX3 = (int) (self.x + self.radius * 0.5) 
        self.PointX4 = (int) (self.x + self.radius) 
        self.PointY1 = self.y
        self.PointY2 = (int) (self.y - self.radius * 1.125)
        self.PointY3 = (int) (self.y + self.radius * 1.125) 
        self.points_x = [0] * 6
        self.points_y = [0] * 6

        self.points_x[0] = self.PointX1
        self.points_x[1] = self.PointX2
        self.points_x[2] = self.PointX3
        self.points_x[3] = self.PointX4
        self.points_x[4] = self.PointX3
        self.points_x[5] = self.PointX2

        self.points_y[0] = self.PointY1
        self.points_y[1] = self.PointY2
        self.points_y[2] = self.PointY2
        self.points_y[3] = self.PointY1
        self.points_y[4] = self.PointY3
        self.points_y[5] = self.PointY3
        
    def compute(self):
        """computes change in hex size, if requested"""
        #over the course of the game we want to shrink the outer hex to reach its "shrink radius"
        #original radius at beginning, shrink radius at end
        
        #how far through are we? 
        percent_time = self.app.gametimer.elapsed() / self.app.config.get_setting('General','game_time')
        
        #scale to new radius based on percent time that's elapsed
        self.radius = self.original_radius - percent_time * (self.original_radius - self.shrink_radius)
        self.set_points(self.radius)
        
    def draw(self,worldsurf):
        """draws hex"""
        for i in range(6):
            pygame.draw.line(worldsurf, self.color, (self.points_x[i], self.points_y[i]), (self.points_x[(i + 1) % 6], self.points_y[(i + 1) % 6]), self.app.linewidth)
            
    def collide(self, ship):
        """tests if point is within convex polygon"""
        #Detecting whether a point is inside a convex polygon can be determined very easily. 
        #Our first step is to create perpendicular vectors for each of the polygon edges and a vector from the test point 
        #to the first vertex of each edge. The perpendicular of a 2D vector can be created by simply creating the vector, 
        #swap the X and Y components, and then negate the X. The dot product of two vectors defines the cosine of the angle between those vectors. 
        #If the dot product for each of the edges is positive, all the angles are less than 90 degrees and the point is inside the polygon. 
        #This is exactly analogous to a 2D version of backface culling for 3D polygons.
        self.line1normal = Vector2D(-(self.points_y[1] - self.points_y[0]), self.points_x[1] - self.points_x[0])
        self.line2normal = Vector2D(-(self.points_y[2] - self.points_y[1]), self.points_x[2] - self.points_x[1])
        self.line3normal = Vector2D(-(self.points_y[3] - self.points_y[2]), self.points_x[3] - self.points_x[2])
        self.line4normal = Vector2D(-(self.points_y[4] - self.points_y[3]), self.points_x[4] - self.points_x[3])
        self.line5normal = Vector2D(-(self.points_y[5] - self.points_y[4]), self.points_x[5] - self.points_x[4])
        self.line6normal = Vector2D(-(self.points_y[0] - self.points_y[5]), self.points_x[0] - self.points_x[5])
        self.pointvector1 = Vector2D(ship.position.x - self.points_x[0], ship.position.y - self.points_y[0])
        self.pointvector2 = Vector2D(ship.position.x - self.points_x[1], ship.position.y - self.points_y[1])
        self.pointvector3 = Vector2D(ship.position.x - self.points_x[2], ship.position.y - self.points_y[2])
        self.pointvector4 = Vector2D(ship.position.x - self.points_x[3], ship.position.y - self.points_y[3])
        self.pointvector5 = Vector2D(ship.position.x - self.points_x[4], ship.position.y - self.points_y[4])
        self.pointvector6 = Vector2D(ship.position.x - self.points_x[5], ship.position.y - self.points_y[5])
        if self.line1normal.dot_product(self.pointvector1) < 0:
            return 0
        elif self.line2normal.dot_product(self.pointvector2) < 0:
            return 0
        elif self.line3normal.dot_product(self.pointvector3) < 0:
            return 0
        elif self.line4normal.dot_product(self.pointvector4) < 0:
            return 0
        elif self.line5normal.dot_product(self.pointvector5) < 0:
            return 0
        elif self.line6normal.dot_product(self.pointvector6) < 0:
            return 0
        else:
            return 1
        