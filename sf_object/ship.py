#ship.py
#this code is to be placed in the "sf_object" subfolder
#Pygame Space Fortress
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2008from __future__ import division
from Vector2D import Vector2D
import math
import sf_object
import pygame
#from frame import Frame

class Ship(sf_object.object.Object):
    """represents the fortress object that typically appears in the center of the worldsurf"""
    def __init__(self, app):
        super(Ship, self).__init__()
        self.app = app
        self.collision_radius = 10
        self.position.x = 245
        self.position.y = 315
        self.orientation = 90
        self.start_position.x = 245
        self.start_position.y = 315
        self.missile_capacity = 100
        self.missile_count = 100
        self.active_missile_limit = 5
        self.active_missile_count = 0
        self.last_fired = -100
        self.last_IFF_value = 0
        self.notify_mine_IFF = False
        self.world_wrap_flag = False
        self.thrust_flag = False
        self.thrust = 0
        self.turn_flag = False
        self.fire_flag = False
        self.turn_speed = 3
        self.acceleration = 0
        self.acceleration_factor = 0.3
        self.velocity_ratio = 0.65
        self.fire_interval = 5
        self.threshold_factor = 0
        self.autofire = False
        self.nochange = False
        self.health = 4
        self.max_vel = 6
        self.set_alive = True
        self.set_invulnerable = False
        self.half_size = 30 #??? What IS this about?
        self.center_line = sf_object.line.Line()
        self.r_wing_line = sf_object.line.Line()
        self.l_wing_line = sf_object.line.Line()
        self.small_hex_flag = False #did we hit the small hex?
        
    def compute(self):
        """updates ship"""
        if self.turn_flag == 'right':
            self.orientation = (self.orientation - self.turn_speed) % 360
        elif self.turn_flag == 'left':
            self.orientation = (self.orientation + self.turn_speed) % 360
        #thrust is only changed if joystick is engaged. Thrust is calculated while processing joystick input
        #self.acceleration = self.thrust * -0.3
        
        if self.thrust_flag == True:
            self.acceleration = self.acceleration_factor
        else:
            self.acceleration = 0
        self.velocity.x += self.acceleration * math.cos(math.radians(self.orientation))
        if self.velocity.x > self.max_vel:
            self.velocity.x = self.max_vel
        elif self.velocity.x < -self.max_vel:
            self.velocity.x = -self.max_vel
        self.velocity.y += self.acceleration * math.sin(math.radians(self.orientation))
        if self.velocity.y > self.max_vel:
            self.velocity.y = self.max_vel
        elif self.velocity.y < -self.max_vel:
            self.velocity.y = -self.max_vel
        self.position.x += self.velocity.x
        self.position.y -= self.velocity.y
        if self.position.x > self.app.WORLD_WIDTH:
            self.position.x = 0
            self.app.score.pnts -= 35
            self.app.log.write("# wrapped right\n")
        if self.position.x < 0:
            self.position.x = self.app.WORLD_WIDTH
            self.app.score.pnts -= 35
            self.app.log.write("# wrapped left\n")
        if self.position.y > self.app.WORLD_HEIGHT:
            self.position.y = 0
            self.app.score.pnts -= 35
            self.app.log.write("# wrapped down\n")
        if self.position.y < 0:
            self.position.y = self.app.WORLD_HEIGHT
            self.app.score.pnts -= 35
            self.app.log.write("# wrapped up\n")
            
    def shoot(self):
        """fires missile"""
        self.app.missile_list.append(sf_object.missile.Missile(self.app))
        self.app.sounds.missile_fired.play()
        if self.app.score.shots > 0:
            self.app.score.shots -= 1
        else:
            self.app.score.pnts -= 3
            
    def draw(self, worldsurf):
        """draw ship to worldsurf"""
        #ship's nose is x+18 to x-18, wings are 18 back and 18 to the side of 0,0
        #NewX = (OldX*Cos(Theta)) - (OldY*Sin(Theta))
        #NewY = -((OldY*Cos(Theta)) + (OldX*Sin(Theta))) - taking inverse because +y is down
        #these formulae rotate about the origin. Need to translate to origin, rotate, and translate back
        self.sinphi = math.sin(math.radians((self.orientation) % 360))
        self.cosphi = math.cos(math.radians((self.orientation) % 360))
        #old x1 = -18
        x1 = -18 * self.cosphi + self.position.x
        y1 = -(-18 * self.sinphi) + self.position.y
        #old x2 = + 18
        x2 = 18 * self.cosphi + self.position.x
        y2 = -(18 * self.sinphi) + self.position.y
        #x3 will be center point
        x3 = self.position.x
        y3 = self.position.y
        #x4, y4 = -18, 18
        x4 = -18 * self.cosphi - 18 * self.sinphi + self.position.x
        y4 = -((18 * self.cosphi) + (-18 * self.sinphi)) + self.position.y
        #x5, y5 = -18, -18
        x5 = -18 * self.cosphi - -18 * self.sinphi + self.position.x
        y5 = -((-18 * self.cosphi) + (-18 * self.sinphi)) + self.position.y
        
        pygame.draw.line(worldsurf, (255,255,0), (x1,y1), (x2,y2))
        pygame.draw.line(worldsurf, (255,255,0), (x3,y3), (x4,y4))
        pygame.draw.line(worldsurf, (255,255,0), (x3,y3), (x5,y5))
        
    def draw2(self,worldsurf):
        """old function to draw ship to worldsurf"""
        self.center_line.x1 = self.position.x + 0.5 * self.half_size * math.sin(math.radians((self.orientation) % 360))
        self.center_line.y1 = self.position.y - 0.5 * self.half_size * math.cos(math.radians((self.orientation) % 360))
        self.center_line.x2 = self.position.x - 0.5 * self.half_size * math.sin(math.radians((self.orientation) % 360))
        self.center_line.y2 = self.position.y + 0.5 * self.half_size * math.cos(math.radians((self.orientation) % 360))

        #Compute Wings
        self.Rwing_headings = (self.orientation + 135) % 360 #225
        self.Lwing_headings = (self.orientation + 225) % 360 #315

        self.l_wing_line.x1 = self.position.x
        self.l_wing_line.y1 = self.position.y
        self.l_wing_line.x2 = self.position.x + 0.707 * self.half_size * math.sin(math.radians(self.Lwing_headings))
        self.l_wing_line.y2 = self.position.y - 0.707 * self.half_size * math.cos(math.radians(self.Lwing_headings))

        self.r_wing_line.x1 = self.position.x
        self.r_wing_line.y1 = self.position.y
        self.r_wing_line.x2 = self.position.x + 0.707 * self.half_size * math.sin(math.radians(self.Rwing_headings))
        self.r_wing_line.y2 = self.position.y - 0.707 * self.half_size * math.cos(math.radians(self.Rwing_headings))
        
        pygame.draw.line(worldsurf, (255,255,0), (self.center_line.x1,self.center_line.y1), \
            (self.center_line.x2,self.center_line.y2))
        pygame.draw.line(worldsurf, (255,255,0), (self.l_wing_line.x1,self.l_wing_line.y1), \
            (self.l_wing_line.x2,self.l_wing_line.y2))
        pygame.draw.line(worldsurf, (255,255,0), (self.r_wing_line.x1,self.r_wing_line.y1), \
            (self.r_wing_line.x2,self.r_wing_line.y2))
