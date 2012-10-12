#mine.py
#this code is to be placed in the "tokens" subfolder
#Space Fortress 5
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2010
from __future__ import division
from vector2D import Vector2D
import math, os
import token
import string
import random
import pygame
import timer
import picture

#from frame import Frame

mine_types = ['gfx/clust1.png', 'gfx/clust2.png', 'gfx/clust3.png', 'gfx/clust4.png']

class Mine(token.Token):
    """represents the friend or foe mine object"""
    def __init__(self, app, type= -1, orientation= -1):
        super(Mine, self).__init__()
        self.position.x = 0 #600
        self.position.y = 0 #400
        self.app = app
        #set random pos
        self.speed = self.app.config['Mine']['mine_speed']
        self.health = 1
        self.alive = True
        self.collision_radius = self.app.config['Mine']['mine_radius'] * self.app.aspect_ratio
        self.foe_probability = self.app.config['Mine']['mine_probability']
        self.iff = None
        self.tagged = "untagged"
        self.color = (0, 255, 255)
        if orientation > -1 and orientation < 360:
            self.orientation = orientation
        else:
            self.orientation = random.randint(0, 359)
        if type > -1 and type < len(mine_types):
            self.type = type
        else:
            self.type = random.choice(range(0, len(mine_types)))
        if self.app.config['Graphics']['fancy']:
            img = mine_types[self.type]
            self.mine = picture.Picture(os.path.join(self.app.approot, img), 64 * self.app.aspect_ratio / 128, self.orientation)
                
    def generate_new_position(self):
        """chooses random location to place mine"""
        self.position.x = random.random() * (self.app.WORLD_WIDTH - 40) + 20
        self.position.y = random.random() * (self.app.WORLD_HEIGHT - 40) + 20
        
    def compute(self):
        """calculates new position of mine"""
        self.velocity.x = math.cos(math.radians((self.to_target_orientation(self.app.ship)) % 360)) * self.speed
        self.velocity.y = -math.sin(math.radians((self.to_target_orientation(self.app.ship)) % 360)) * self.speed
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y
        
    def draw(self, worldsurf):
        """draws mine to worldsurf"""
        if self.app.config['Graphics']['fancy']:
            self.mine.rect.centerx = self.position.x
            self.mine.rect.centery = self.position.y
            worldsurf.blit(self.mine.image, self.mine.rect)
        else:
            pygame.draw.line(worldsurf, self.color, (self.position.x - 16 * self.app.aspect_ratio, self.position.y), (self.position.x, self.position.y - 24 * self.app.aspect_ratio), self.app.linewidth)
            pygame.draw.line(worldsurf, self.color, (self.position.x, self.position.y - 24 * self.app.aspect_ratio), (self.position.x + 16 * self.app.aspect_ratio, self.position.y), self.app.linewidth)
            pygame.draw.line(worldsurf, self.color, (self.position.x + 16 * self.app.aspect_ratio, self.position.y), (self.position.x, self.position.y + 24 * self.app.aspect_ratio), self.app.linewidth)
            pygame.draw.line(worldsurf, self.color, (self.position.x, self.position.y + 24 * self.app.aspect_ratio), (self.position.x - 16 * self.app.aspect_ratio, self.position.y), self.app.linewidth)

    def __str__(self):
        return '(%.2f,%.2f,%d,%.2f)' % (self.position.x, self.position.y, self.type, self.orientation)

class MineList(list):
    """extension of list to contain properties for mine subsystem"""
    def __init__(self, app):
        super(MineList, self).__init__()
        self.app = app
        self.mine_count = 0
        self.mine_mode = self.app.config['Mine']['mine_mode']
        self.minimum_spawn_distance = self.app.config['Mine']['minimum_spawn_distance']
        self.maximum_spawn_distance = self.app.config['Mine']['maximum_spawn_distance']
        self.iff_lower_bound = self.app.config['Mine']['intrvl_min']
        self.iff_upper_bound = self.app.config['Mine']['intrvl_max']
        self.num_foes = self.app.config['Mine']['num_foes']
        self.letters = list(string.letters[26:]) #list of uppercase letters
        self.generate_foes()
        self.timeout = self.app.config['Mine']['mine_timeout'] #milliseconds after spawn when mine "gives up"
        self.spawn_time = self.app.config['Mine']['mine_spawn'] #milliseconds after destruction when mine "respawns"
        self.timer = timer.Timer(self.app.gametimer.elapsed)
        self.flag = False #for timer, to determine state of standard mine
        self.iff_timer = timer.Timer(self.app.gametimer.elapsed)
        self.iff_flag = False #are we in the middle of trying to identify a foe mine?
        #MOT constants
        self.f = pygame.font.Font(self.app.fp, 14)
        self.MOT_count = self.app.config['MOT']['MOT_count']
        self.MOT_state = "off" #states are off, onset, move, identify
        self.MOT_off_time = self.app.config['MOT']['MOT_off_time']
        self.MOT_onset_time = self.app.config['MOT']['MOT_onset_time']
        self.MOT_move_time = self.app.config['MOT']['MOT_move_time']
        self.MOT_switch_time = self.app.config['MOT']['MOT_switch_time']
        self.MOT_max_deflection = self.app.config['MOT']['MOT_max_deflection']
        self.MOT_movement_style = self.app.config['MOT']['MOT_movement_style']
        self.MOT_identification_time = self.app.config['MOT']['MOT_identification_time']
        self.MOT_identification_type = self.app.config['MOT']['MOT_identification_type']
        self.MOT_timer = timer.Timer(self.app.gametimer.elapsed) #determines when MOT mines change state
        self.MOT_switch_timer = timer.Timer(self.app.gametimer.elapsed) #determine when moving MOT mine changes direction
        
    def generate_foes(self):
        """determine which mine designations are 'foes'"""
        self.foe_letters = random.sample(self.letters, self.num_foes)
            
    def add(self):
        """adds new mine to list"""
        if self.mine_mode == "standard":
            mine = Mine(self.app)
        else:
            mine = MOTMine(self.app)
        mine.generate_new_position()
        while (mine.get_distance_to_object(self.app.ship) < self.minimum_spawn_distance) or (mine.get_distance_to_object(self.app.ship) > self.maximum_spawn_distance):
            mine.generate_new_position()
        if random.random() < mine.foe_probability:
            mine.iff = random.sample(self.foe_letters, 1)[0]
        else:
            mine.iff = random.sample(self.letters, 1)[0]
        if self.mine_mode == "standard":
            self.app.score.iff = mine.iff
        self.mine_count += 1
        self.append(mine)
        
    def compute(self):
        """computes all mines"""
        if self.mine_mode == "standard":
            for mine in self:
                mine.compute()
        elif self.mine_mode == "MOT":
            #check state and timer and act accordingly. States are off, onset, move, identify
            if self.MOT_state == "off" and self.MOT_timer.elapsed() > self.MOT_off_time:
                self.MOT_state = "onset"
                self.color = (0, 255, 255)
                for i in range(self.MOT_count - 1):
                    self.add()
                self.MOT_timer.reset()
            if self.MOT_state == "onset" and self.MOT_timer.elapsed() > self.MOT_onset_time:
                self.MOT_state = "moving"
                self.MOT_timer.reset()
                self.MOT_switch_timer.reset()
            if self.MOT_state == "moving" and self.MOT_timer.elapsed() < self.MOT_move_time:
                for i, mine in enumerate(self):
                    mine.compute()
                    if self.MOT_movement_style == "warp":
                        if mine.position.x > self.app.WORLD_WIDTH:
                            mine.position.x = 0
                            mine.app.gameevents.add("mine%d_warp" % i, "right")
                        if mine.position.x < 0:
                            mine.position.x = self.app.WORLD_WIDTH
                            mine.app.gameevents.add("mine%d_warp" % i, "left")
                        if mine.position.y > self.app.WORLD_HEIGHT:
                            mine.position.y = 0
                            mine.app.gameevents.add("mine%d_warp" % i, "down")
                        if mine.position.y < 0:
                            mine.position.y = self.app.WORLD_HEIGHT
                            mine.app.gameevents.add("mine%d_warp" % i, "up")
                    elif self.MOT_movement_style == "bounce":
                        if mine.position.x > self.app.WORLD_WIDTH - 10:
                            mine.vec.x *= -1
                            mine.app.gameevents.add("mine%d_bounce" % i, "right")
                        if mine.position.x < 10:
                            mine.vec.x *= -1
                            mine.app.gameevents.add("mine%d_bounce" % i, "left")
                        if mine.position.y > self.app.WORLD_HEIGHT - 10:
                            mine.vec.y *= -1
                            mine.app.gameevents.add("mine%d_bounce" % i, "down")
                        if mine.position.y < 10:
                            mine.vec.y *= -1
                            mine.app.gameevents.add("mine%d_bounce" % i, "up")
            if self.MOT_state == "moving" and self.MOT_timer.elapsed() > self.MOT_move_time:
                self.MOT_state = "identify"
                self.MOT_timer.reset()
                #change some to red
                for i, item in enumerate(self):
                    if (random.randint(0, 1)):
                        self[i].color = (255, 0, 0)
                
            if self.MOT_state == "identify" and self.MOT_timer.elapsed() > self.MOT_identification_time:
                self.MOT_state = "off"
                for i, item in enumerate(self):
                    del self[i]
            
    def draw(self):
        """draws all mines"""
        for mine in self:
            mine.draw(self.app.worldsurf)
            if self.MOT_state == "onset":
                tag = self.f.render(mine.iff, 0, (255, 255, 0))
                tag_rect = tag.get_rect()
                tag_rect.centerx = mine.position.x
                tag_rect.centery = mine.position.y
                self.app.worldsurf.blit(tag, tag_rect)
                
    def __str__(self):
        s = ''
        for i in range(0, len(self)):
            s = '%s,%s' % (s, self[i])
        return '[%s]' % (s[1:])

class MOTMine(Mine):
    """A mine that moves in a MOT paradigm"""
    def __init__(self, app):
        super(MOTMine, self).__init__(app)
        self.app = app
        #set trajectory to random normal vector and scale to speed
        self.vec = Vector2D.random2D()
        self.vec.scalar_product(self.speed)
        
    def compute(self):
        """calculates new position of mine"""
        self.position.x += self.vec.x
        self.position.y += self.vec.y
        
        