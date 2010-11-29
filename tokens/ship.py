#ship.py
#this code is to be placed in the "tokens" subfolder
#Space Fortress 5
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2010
import math
import token
import missile
import pygame
from timer import Timer
from gameevent import GameEvent

class Ship(token.Token):
    """represents the fortress object that typically appears in the center of the worldsurf"""
    def __init__(self, app):
        super(Ship, self).__init__()
        self.app = app
        self.collision_radius = int(app.config["ship_radius"])
        self.position.x = int(app.config["ship_pos_x"])
        self.position.y = int(app.config["ship_pos_y"])
        self.velocity.x = int(app.config["ship_vel_x"])
        self.velocity.y = int(app.config["ship_vel_y"])
        self.orientation = int(app.config["ship_orientation"])
        self.missile_capacity = int(app.config["missile_max"])
        self.missile_count = int(app.config["missile_num"])
        self.thrust_flag = False
        self.thrust = 0
        self.turn_flag = False
        self.fire_flag = False
        self.turn_speed = int(app.config["ship_turn_speed"])
        self.acceleration = 0
        self.acceleration_factor = float(app.config["ship_acceleration"])
        self.start_health = int(app.config["ship_hit_points"])
        self.health = int(app.config["ship_hit_points"])
        self.max_vel = int(app.config["ship_max_vel"])
        self.alive = True
        self.small_hex_flag = False #did we hit the small hex?
        self.shot_timer = Timer() #time between shots, for VLNER assessment
        
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
            self.app.gameevents.append(GameEvent("warp", "right"))
        if self.position.x < 0:
            self.position.x = self.app.WORLD_WIDTH
            self.app.gameevents.append(GameEvent("warp", "left"))
        if self.position.y > self.app.WORLD_HEIGHT:
            self.position.y = 0
            self.app.gameevents.append(GameEvent("warp", "down"))
        if self.position.y < 0:
            self.position.y = self.app.WORLD_HEIGHT
            self.app.gameevents.append(GameEvent("warp", "up"))
            
    def fire(self):
        """fires missile"""
        self.app.missile_list.append(missile.Missile(self.app))
        self.app.sounds.missile_fired.play()
        if self.app.score.shots > 0:
            self.app.score.shots -= 1
        else:
            self.app.score.pnts -= int(self.app.config["missile_penalty"])
            self.app.score.bonus -= int(self.app.config["missile_penalty"])
            
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
        
        pygame.draw.line(worldsurf, (255,255,0), (x1,y1), (x2,y2), self.app.linewidth)
        pygame.draw.line(worldsurf, (255,255,0), (x3,y3), (x4,y4), self.app.linewidth)
        pygame.draw.line(worldsurf, (255,255,0), (x3,y3), (x5,y5), self.app.linewidth)
 
