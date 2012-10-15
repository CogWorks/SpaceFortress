import math, os
import missile
import pygame
import picture
from timer import Timer
from gameevent import GameEvent
from sftoken import Token

import pkg_resources

import pygl2d

class Ship(Token):
    """represents the fortress object that typically appears in the center of the worldsurf"""
    def __init__(self, app):
        super(Ship, self).__init__()
        self.app = app
        self.collision_radius = self.app.config['Ship']['ship_radius'] * self.app.aspect_ratio
        self.position.x = self.app.world.left + self.app.config['Ship']['ship_pos_x'] * self.app.aspect_ratio
        self.position.y = self.app.world.top + self.app.config['Ship']['ship_pos_y'] * self.app.aspect_ratio
        self.nose = (self.position.x, self.position.y)
        self.velocity.x = self.app.config['Ship']['ship_vel_x']
        self.velocity.y = self.app.config['Ship']['ship_vel_y']
        self.orientation = self.app.config['Ship']['ship_orientation']
        self.missile_capacity = self.app.config['Missile']['missile_max']
        self.missile_count = self.app.config['Missile']['missile_num']
        self.thrust_flag = False
        self.thrust = 0
        self.turn_left_flag = False
        self.turn_right_flag = False
        self.fire_flag = False
        self.turn_speed = self.app.config['Ship']['ship_turn_speed']
        self.acceleration = 0
        self.acceleration_factor = self.app.config['Ship']['ship_acceleration']
        self.start_health = self.app.config['Ship']['ship_hit_points']
        self.health = self.app.config['Ship']['ship_hit_points']
        self.max_vel = self.app.config['Ship']['ship_max_vel']
        self.alive = True
        self.small_hex_flag = False #did we hit the small hex?
        self.shot_timer = Timer(self.app.gametimer.elapsed) #time between shots, for VLNER assessment
        self.joy_turn = 0.0
        self.joy_thrust = 0.0
        self.invert_x = 1.0
        if self.app.config['Joystick']['invert_x']:
            self.invert_x = -1.0
        self.invert_y = 1.0
        if self.app.config['Joystick']['invert_y']:
            self.invert_y = -1.0
        self.color = (255, 255, 0)
        if self.app.config['Graphics']['fancy']:
            self.ship = pygl2d.image.Image(pkg_resources.resource_stream("resources", 'gfx/ship.png'))
            self.ship2 = pygl2d.image.Image(pkg_resources.resource_stream("resources", 'gfx/ship2.png'))
            self.ship_rect = self.ship.get_rect()
            self.ship.scale(66 * self.app.aspect_ratio / 175)
            self.ship2.scale(66 * self.app.aspect_ratio / 175)
            self.shields = []
            for i in range(0, self.start_health):
                shield = pygl2d.image.Image(pkg_resources.resource_stream("resources", 'gfx/shield.png'))
                shield.colorize(255.0, 255.0, 255.0, int(255.0 / (self.start_health - 1) * i))
                self.shield_rect = shield.get_rect()
                shield.scale(70 * self.app.aspect_ratio / 400)
                self.shields.append(shield)


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
        if self.position.x > self.app.world.right:
            self.position.x = self.app.world.left
            self.app.gameevents.add("warp", "right")
        if self.position.x < self.app.world.left:
            self.position.x = self.app.world.right
            self.app.gameevents.add("warp", "left")
        if self.position.y > self.app.world.bottom:
            self.position.y = self.app.world.top
            self.app.gameevents.add("warp", "down")
        if self.position.y < self.app.world.top:
            self.position.y = self.app.world.bottom
            self.app.gameevents.add("warp", "up")

    def fire(self):
        """fires missile"""
        if self.app.config['General']['next_gen']:
            if self.app.score.shots > 0:
                self.app.missile_list.append(missile.Missile(self.app))
                self.app.snd_missile_fired.play()
                self.app.score.shots -= 1
            else:
                self.app.snd_empty.play()
                if self.app.config['Missile']['empty_penalty']:
                    self.app.score.pnts -= self.app.config['Missile']['missile_penalty']
                    self.app.score.bonus -= self.app.config['Missile']['missile_penalty']
        else:
            self.app.missile_list.append(missile.Missile(self.app))
            self.app.snd_missile_fired.play()
            if self.app.score.shots > 0:
                self.app.score.shots -= 1
            else:
                self.app.snd_empty.play()
                self.app.score.pnts -= self.app.config['Missile']['missile_penalty']
                self.app.score.bonus -= self.app.config['Missile']['missile_penalty']

    def draw(self):
        """draw ship to worldsurf"""
        if self.app.config['Graphics']['fancy']:
            if not self.thrust_flag:
                ship = self.ship
            else:
                ship = self.ship2
            ship.rotate(self.orientation - 90)
            self.ship_rect.center = (self.position.x, self.position.y)
            ship.draw(self.ship_rect.topleft)
            self.shield_rect.center = (self.position.x, self.position.y)
            self.shields[self.health - 1].draw(self.shield_rect)
        else:
            sinphi = math.sin(math.radians((self.orientation) % 360))
            cosphi = math.cos(math.radians((self.orientation) % 360))
            x1 = -18 * cosphi * self.app.aspect_ratio + self.position.x
            y1 = -(-18 * sinphi) * self.app.aspect_ratio + self.position.y
            x2 = 18 * cosphi * self.app.aspect_ratio + self.position.x
            y2 = -(18 * sinphi) * self.app.aspect_ratio + self.position.y
            self.nose = (x2, y2)
            x3 = self.position.x
            y3 = self.position.y
            x4 = (-18 * cosphi - 18 * sinphi) * self.app.aspect_ratio + self.position.x
            y4 = (-((18 * cosphi) + (-18 * sinphi))) * self.app.aspect_ratio + self.position.y
            x5 = (-18 * cosphi - -18 * sinphi) * self.app.aspect_ratio + self.position.x
            y5 = (-((-18 * cosphi) + (-18 * sinphi))) * self.app.aspect_ratio + self.position.y
            pygl2d.draw.line((x1, y1), (x2, y2), self.color, self.app.linewidth)
            pygl2d.draw.line((x3, y3), (x4, y4), self.color, self.app.linewidth)
            pygl2d.draw.line((x3, y3), (x5, y5), self.color, self.app.linewidth)
