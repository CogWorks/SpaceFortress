#ship.py
#this code is to be placed in the "tokens" subfolder
#Space Fortress 5
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2010
import math, os
import token
import missile
import pygame
import picture
from timer import Timer
from gameevent import GameEvent

class Ship(token.Token):
    """represents the fortress object that typically appears in the center of the worldsurf"""
    def __init__(self, app):
        super(Ship, self).__init__()
        self.app = app
        self.collision_radius = self.app.config.get_setting('Ship','ship_radius')*self.app.aspect_ratio
        self.position.x = self.app.config.get_setting('Ship','ship_pos_x')*self.app.aspect_ratio
        self.position.y = self.app.config.get_setting('Ship','ship_pos_y')*self.app.aspect_ratio
        self.nose = (self.position.x, self.position.y)
        self.velocity.x = self.app.config.get_setting('Ship','ship_vel_x')
        self.velocity.y = self.app.config.get_setting('Ship','ship_vel_y')
        self.orientation = self.app.config.get_setting('Ship','ship_orientation')
        self.missile_capacity = self.app.config.get_setting('Missile','missile_max')
        self.missile_count = self.app.config.get_setting('Missile','missile_num')
        self.thrust_flag = False
        self.thrust = 0
        self.turn_left_flag = False
        self.turn_right_flag = False
        self.fire_flag = False
        self.turn_speed = self.app.config.get_setting('Ship','ship_turn_speed')
        self.acceleration = 0
        self.acceleration_factor = self.app.config.get_setting('Ship','ship_acceleration')
        self.start_health = self.app.config.get_setting('Ship','ship_hit_points')
        self.health = self.app.config.get_setting('Ship','ship_hit_points')
        self.max_vel = self.app.config.get_setting('Ship','ship_max_vel')
        self.alive = True
        self.small_hex_flag = False #did we hit the small hex?
        self.shot_timer = Timer() #time between shots, for VLNER assessment
        self.joy_turn = 0.0
        self.joy_thrust = 0.0
        self.invert_x = 1.0
        if self.app.config.get_setting('Joystick','invert_x'):
            self.invert_x = -1.0
        self.invert_y = 1.0
        if self.app.config.get_setting('Joystick','invert_y'):
            self.invert_y = -1.0
        self.color = (255,255,0)
        if self.app.config.get_setting('Graphics','fancy'):
            self.ship = picture.Picture(os.path.join(self.app.approot, 'gfx/ship.png'), 48*self.app.aspect_ratio/128)
            self.ship2 = picture.Picture(os.path.join(self.app.approot, 'gfx/ship2.png'), 66*self.app.aspect_ratio/175)
            self.shields = []
            for i in range(0,self.start_health):
                self.shields.append(picture.Picture(os.path.join(self.app.approot, 'gfx/shield.png'),
                                                    70*self.app.aspect_ratio/400,
                                                    alpha=int(255.0 / (self.start_health-1) * i)))


    def compute(self):
        """updates ship"""
        if self.app.joystick:
            self.orientation = (self.orientation - self.turn_speed * self.joy_turn * self.invert_x) % 360
        else:
            if self.turn_right_flag:
                self.orientation = (self.orientation - self.turn_speed) % 360
            if self.turn_left_flag:
                self.orientation = (self.orientation + self.turn_speed) % 360
        #thrust is only changed if joystick is engaged. Thrust is calculated while processing joystick input
        #self.acceleration = self.thrust * -0.3

        if self.app.joystick:
            if self.joy_thrust * self.invert_y > 0:
                self.acceleration = self.acceleration_factor * self.joy_thrust * self.invert_y
            else:
                self.acceleration = 0
        else:
            if self.thrust_flag == True:
                self.acceleration = self.acceleration_factor
            else:
                self.acceleration = 0

        self.velocity.x += self.acceleration * math.cos(math.radians(self.orientation))
        self.velocity.y += self.acceleration * math.sin(math.radians(self.orientation))

        if self.velocity.x > self.max_vel:
            self.velocity.x = self.max_vel
        elif self.velocity.x < -self.max_vel:
            self.velocity.x = -self.max_vel

        if self.velocity.y > self.max_vel:
            self.velocity.y = self.max_vel
        elif self.velocity.y < -self.max_vel:
            self.velocity.y = -self.max_vel
        self.position.x += self.velocity.x
        self.position.y -= self.velocity.y
        if self.position.x > self.app.WORLD_WIDTH:
            self.position.x = 0
            self.app.gameevents.add("warp", "right")
        if self.position.x < 0:
            self.position.x = self.app.WORLD_WIDTH
            self.app.gameevents.add("warp", "left")
        if self.position.y > self.app.WORLD_HEIGHT:
            self.position.y = 0
            self.app.gameevents.add("warp", "down")
        if self.position.y < 0:
            self.position.y = self.app.WORLD_HEIGHT
            self.app.gameevents.add("warp", "up")

    def fire(self):
        """fires missile"""
        if self.app.config.get_setting('General','next_gen'):
            if self.app.score.shots > 0:
                self.app.missile_list.append(missile.Missile(self.app))
                self.app.sounds.missile_fired.play()
                self.app.score.shots -= 1
            else:
                self.app.sounds.empty.play()
                if self.app.config.get_setting('Missile','empty_penalty'):
                    self.app.score.pnts -= self.app.config.get_setting('Missile','missile_penalty')
                    self.app.score.bonus -= self.app.config.get_setting('Missile','missile_penalty')
        else:
            self.app.missile_list.append(missile.Missile(self.app))
            self.app.sounds.missile_fired.play()
            if self.app.score.shots > 0:
                self.app.score.shots -= 1
            else:
                self.app.sounds.empty.play()
                self.app.score.pnts -= self.app.config.get_setting('Missile','missile_penalty')
                self.app.score.bonus -= self.app.config.get_setting('Missile','missile_penalty')

    def draw(self, worldsurf):
        """draw ship to worldsurf"""
        #ship's nose is x+18 to x-18, wings are 18 back and 18 to the side of 0,0
        #NewX = (OldX*Cos(Theta)) - (OldY*Sin(Theta))
        #NewY = -((OldY*Cos(Theta)) + (OldX*Sin(Theta))) - taking inverse because +y is down
        #these formulae rotate about the origin. Need to translate to origin, rotate, and translate back
        self.sinphi = math.sin(math.radians((self.orientation) % 360))
        self.cosphi = math.cos(math.radians((self.orientation) % 360))
        #old x1 = -18
        x1 = -18 * self.cosphi * self.app.aspect_ratio + self.position.x
        y1 = -(-18 * self.sinphi) * self.app.aspect_ratio + self.position.y
        #old x2 = + 18
        x2 = 18 * self.cosphi * self.app.aspect_ratio + self.position.x
        y2 = -(18 * self.sinphi) * self.app.aspect_ratio + self.position.y
        # nose
        self.nose = (x2,y2)
        #x3 will be center point
        x3 = self.position.x
        y3 = self.position.y
        #x4, y4 = -18, 18
        x4 = (-18 * self.cosphi - 18 * self.sinphi)*self.app.aspect_ratio + self.position.x
        y4 = (-((18 * self.cosphi) + (-18 * self.sinphi)))*self.app.aspect_ratio + self.position.y
        #x5, y5 = -18, -18
        x5 = (-18 * self.cosphi - -18 * self.sinphi)*self.app.aspect_ratio + self.position.x
        y5 = (-((-18 * self.cosphi) + (-18 * self.sinphi)))*self.app.aspect_ratio + self.position.y

        if self.app.config.get_setting('Graphics','fancy'):
            if not self.thrust_flag:
                ship = pygame.transform.rotate(self.ship.image, self.orientation-90)
            else:
                ship = pygame.transform.rotate(self.ship2.image, self.orientation-90)
            shiprect = ship.get_rect()
            shiprect.centerx = self.position.x
            shiprect.centery = self.position.y
            worldsurf.blit(ship, shiprect)
            if self.app.playback and self.app.playback_logver <= 4:
                pass
            else:
                s = self.health-1
                self.shields[s].rect.centerx = self.position.x
                self.shields[s].rect.centery = self.position.y
                worldsurf.blit(self.shields[s].image, self.shields[s].rect)
        else:
            pygame.draw.line(worldsurf, self.color, (x1,y1), (x2,y2), self.app.linewidth)
            pygame.draw.line(worldsurf, self.color, (x3,y3), (x4,y4), self.app.linewidth)
            pygame.draw.line(worldsurf, self.color, (x3,y3), (x5,y5), self.app.linewidth)
