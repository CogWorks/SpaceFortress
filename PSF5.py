from __future__ import division
import tokens
from tokens.gameevent import *
import sounds
import sys, os
import pygame

release_build = False

class Game(object):
    """Main game application"""
    def __init__(self):
        super(Game, self).__init__()
        pygame.init()
        self.config = {}
        if sys.platform == "darwin" and release_build:
            self.app_path = '../../../'
        else:
            self.app_path = '.'
        self.datapath = os.path.join(self.app_path, "data/")
        configfile = open(os.path.join(self.app_path, "config.txt"))
        configlog = configfile.readlines()
        for line in configlog:
            if line[0] in ["#", "\n"]:
                pass
            else:
                command = line.rstrip().split()
                if len(command) > 2:
                    self.config[command[0]] = command[1:]
                else:
                    self.config[command[0]] = command[1]
        configfile.close()
        self.SCREEN_WIDTH = 1024
        self.SCREEN_HEIGHT = 768
        self.WORLD_WIDTH = 710
        self.WORLD_HEIGHT = 626
        self.linewidth = int(self.config["linewidth"])
        self.frame = tokens.frame.Frame(self.config)
        self.score = tokens.score.Score(self.config)
        self.f = pygame.font.Font("fonts/freesansbold.ttf", 14)
        self.f24 = pygame.font.Font("fonts/freesansbold.ttf", 20)
        self.f96 = pygame.font.Font("fonts/freesansbold.ttf", 72)
        self.f36 = pygame.font.Font("fonts/freesansbold.ttf", 36)
        self.thrust_key = eval("pygame.K_%s"%self.config["thrust_key"])
        self.left_turn_key = eval("pygame.K_%s"%self.config["left_turn_key"])
        self.right_turn_key = eval("pygame.K_%s"%self.config["right_turn_key"])
        self.fire_key = eval("pygame.K_%s"%self.config["fire_key"])
        self.IFF_key = eval("pygame.K_%s"%self.config["IFF_key"])
        self.shots_key = eval("pygame.K_%s"%self.config["shots_key"])
        self.pnts_key = eval("pygame.K_%s"%self.config["pnts_key"])
        self.vector_explosion = pygame.image.load("gfx/exp.png")
        self.vector_explosion.set_colorkey((0, 0, 0))
        self.vector_explosion_rect = self.vector_explosion.get_rect()
        self.sounds = sounds.Sounds()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.gametimer = tokens.timer.Timer()
        self.flighttimer = tokens.timer.Timer()
    
   
    def setup_world(self):
        """initializes gameplay screen"""
        self.worldsurf = pygame.Surface((self.WORLD_WIDTH, self.WORLD_HEIGHT))
        self.worldrect = self.worldsurf.get_rect()
        self.worldrect.centerx = self.SCREEN_WIDTH/2
        if self.config["new_scoring_pos"] == "f":
            self.worldrect.top = 5
            self.scoresurf = pygame.Surface((self.WORLD_WIDTH, 64))
            self.scorerect = self.scoresurf.get_rect()
            self.scorerect.top = 634
            self.scorerect.centerx = self.SCREEN_WIDTH/2
        else:
            self.worldrect.top = 70
            self.scoresurf = pygame.Surface.copy(self.screen)
            self.scorerect = self.screen.get_rect()
            #self.scorerect.top = 5
        self.gameevents = GameEventList()
        self.missile_list = []
        self.shell_list = []
        self.ship = tokens.ship.Ship(self)
        if self.config["bonus_exists"] == "t":
            self.bonus = tokens.bonus.Bonus(self)
            self.bonus_exists = True
        else:
            self.bonus_exists = False
        if self.config["fortress_exists"] == "t":
            self.fortress = tokens.fortress.Fortress(self)
            self.fortress_exists = True
        else:
            self.fortress.exists = False
        self.bighex = tokens.hexagon.Hex(self, int(self.config["big_hex"]))
        self.smallhex = tokens.hexagon.Hex(self,int(self.config["small_hex"]))
        self.gametimer.reset()
        self.flighttimer.reset()
        
    
    def process_input(self):
        """creates game events based on pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.gameevents.add("press", "quit")
                elif event.key == self.thrust_key:
                    self.gameevents.add("press", "thrust")
                elif event.key == self.left_turn_key:
                    self.gameevents.add("press", "left")
                elif event.key == self.right_turn_key:
                    self.gameevents.add("press", "right")
                elif event.key == self.fire_key:
                    self.gameevents.add("press", "fire")
                elif event.key == self.IFF_key:
                    self.gameevents.add("press", "IFF")
                elif event.key == self.shots_key:
                    self.gameevents.add("press", "shots")
                elif event.key == self.pnts_key:
                    self.gameevents.add("press", "pnts")
            elif event.type == pygame.KEYUP:
                if event.key == self.thrust_key:
                    self.gameevents.add("release", "thrust")
                elif event.key == self.left_turn_key:
                    self.gameevents.add("release", "left")
                elif event.key == self.right_turn_key:
                    self.gameevents.add("release", "right")
                elif event.key == self.fire_key:
                    self.gameevents.add("release", "fire")
                elif event.key == self.IFF_key:
                    self.gameevents.add("release", "IFF")
                elif event.key == self.shots_key:
                    self.gameevents.add("release", "shots")
                elif event.key == self.pnts_key:
                    self.gameevents.add("release", "pnts")
    
    def process_game_logic(self):
        """processes game logic to produce game events"""
        self.ship.compute()
        for missile in self.missile_list:
            missile.compute()
        if self.fortress_exists == True:
            self.fortress.compute()
        for shell in self.shell_list:
            shell.compute()
        if self.config["hex_shrink"] == "t":
            self.bighex.compute()
        self.check_bounds()
        #test collisions to generate game events
        self.test_collisions()
        if self.flighttimer.elapsed() > int(self.config["update_timer"]):
            self.flighttimer.reset()
            if (self.ship.velocity.x **2 + self.ship.velocity.y **2)**0.5 < int(self.config["speed_threshold"]):
                self.score.vlcty += int(self.config["VLCTY_increment"])
                self.score.flight += int(self.config["VLCTY_increment"])
            else:
                self.score.vlcty -= int(self.config["VLCTY_increment"])
                self.score.flight -= int(self.config["VLCTY_increment"])
            if self.bighex.collide(self.ship):
                self.score.cntrl += int(self.config["CNTRL_increment"])
                self.score.flight += int(self.config["CNTRL_increment"])
            else:
                self.score.cntrl += int(self.config["CNTRL_increment"])/2
        if self.bonus_exists:
            if self.bonus.visible == False and self.bonus.timer.elapsed() > int(self.config["symbol_down_time"]):
                self.gameevents.add("activate", "bonus")
            elif self.bonus.visible == True and self.bonus.timer.elapsed() >= int(self.config["symbol_up_time"]):
                self.gameevents.add("deactivate", "bonus")
            
    def process_events(self):
        """processes internal list of game events for this frame"""
        while len(self.gameevents) > 0:
            currentevent = self.gameevents.pop(0)
            command = currentevent.command
            obj = currentevent.obj
            target = currentevent.target
            print "command %s, object %s, target %s"%(command, obj, target)
            if command == "press":    
                if obj == "quit":
                    sys.exit(0)
                elif obj == "left":
                    self.ship.turn_flag = "left"
                elif obj == "right":
                    self.ship.turn_flag = "right"
                elif obj == "thrust":
                    self.ship.thrust_flag = True
                elif obj == "fire":
                    self.ship.fire()
            elif command == "release":
                if obj == "left" or obj == "right":
                    self.ship.turn_flag = False
                elif obj == "thrust":
                    self.ship.thrust_flag = False
            elif command == "warp":
                self.score.pnts -= int(self.config["warp_penalty"])
                self.score.flight -= int(self.config["warp_penalty"])
            elif command == "collide":
                if obj == "small_hex" and not self.smallhex.small_hex_flag:
                    self.ship.velocity.x = -self.ship.velocity.x
                    self.ship.velocity.y = -self.ship.velocity.y
                    self.score.pnts -= int(self.config["small_hex_penalty"])
                    self.score.flight -= int(self.config["small_hex_penalty"])
                    self.smallhex.small_hex_flag = True
                if obj == "shell":
                    #remove shell, target is index
                    del self.shell_list[target]
                    self.score.pnts -= int(self.config["shell_hit_penalty"])
                    self.score.fortress -= int(self.config["shell_hit_penalty"])
                    self.ship.take_damage()
                    if not self.ship.alive:
                        self.gameevents.add("destroyed", "ship", "shell")
                        self.score.pnts -= int(self.config["ship_death_penalty"])
                        self.score.fortress -= int(self.config["ship_death_penalty"])
                if obj == "missile":
                    if target == "fortress":
                        if self.ship.shot_timer.elapsed() >= int(self.config["vlner_time"]): #adjust for mine later
                            self.score.vlner += 1
                            self.gameevents.add("VLNER++")
                        if self.ship.shot_timer.elapsed() < int(self.config["vlner_time"]) and self.score.vlner >= int(self.config["vlner_threshold"]): #adjust for mine later
                            self.gameevents.add("destroyed", "fortress")
                            self.fortress.alive = False
                            self.fortress.reset_timer.reset()
                            self.sounds.explosion.play()
                            self.score.pnts += int(self.config["destroy_fortress"])
                            self.score.fortress += int(self.config["destroy_fortress"])
                            self.score.vlner = 0
                        if self.ship.shot_timer.elapsed() < int(self.config["vlner_time"]) and self.score.vlner < int(self.config["vlner_threshold"]):
                            self.gameevents.add("reset", "VLNER")
                            self.score.vlner = 0
                            self.sounds.vlner_reset.play()
                        self.ship.shot_timer.reset()
            elif command == "activate":
                if obj == "bonus":
                    self.bonus.visible = True
                    self.bonus.timer.reset()
                    self.bonus.prior_symbol = self.bonus.current_symbol
                    self.bonus.get_new_symbol()
            elif command == "deactivate":
                if obj == "bonus":
                    self.bonus.visible = False
                    self.bonus.timer.reset()
                           
                                            
    def test_collisions(self):
        """test collisions between relevant game entities"""
        if self.smallhex.collide(self.ship):
            self.gameevents.add("collide", "small_hex", "ship")
        else:
            self.smallhex.small_hex_flag = False
        for i, shell in enumerate(self.shell_list):
            if shell.collide(self.ship):
                self.gameevents.add("collide", "shell", i)
        for i, missile in enumerate(self.missile_list):
            if missile.collide(self.fortress):
                del self.missile_list[i]
                self.gameevents.add("collide", "missile", "fortress")
    
                
    def check_bounds(self):
        """determine whether any shells or missiles have left the world"""
        width = self.WORLD_WIDTH
        height = self.WORLD_HEIGHT
        for i, missile in enumerate(self.missile_list):
            if missile.out_of_bounds(width, height):
                del self.missile_list[i]
                self.gameevents.add("bounds_remove", "missile")
        for i, shell in enumerate(self.shell_list):
            if shell.out_of_bounds(width, height):
                del self.shell_list[i]
                self.gameevents.add("bounds_remove", "shell")
    
        
    def reset_position(self):
        """pauses the game and resets"""
        self.sounds.explosion.play()
        pygame.time.delay(1000)
        self.score.iff = ""
        self.ship.alive = True
        self.ship.position.x = int(self.config["ship_pos_x"])
        self.ship.position.y = int(self.config["ship_pos_y"])
        self.ship.velocity.x = int(self.config["ship_vel_x"])
        self.ship.velocity.y = int(self.config["ship_vel_y"])
        self.ship.orientation = int(self.config["ship_orientation"])
    
    def draw(self):
        """draws the world"""
        self.screen.fill((0,0,0))
        self.frame.draw(self.worldsurf, self.scoresurf)
        self.score.draw(self.scoresurf)
        self.bighex.draw(self.worldsurf)
        self.smallhex.draw(self.worldsurf)
        for shell in self.shell_list:
            shell.draw(self.worldsurf)
        if self.fortress_exists:
            if self.fortress.alive:
                self.fortress.draw(self.worldsurf)
            else:
                self.vector_explosion_rect.center = (self.fortress.position.x, self.fortress.position.y)
                self.worldsurf.blit(self.vector_explosion, self.vector_explosion_rect)
        for missile in self.missile_list:
            missile.draw(self.worldsurf)
        if self.ship.alive:
            self.ship.draw(self.worldsurf)
        else:
            self.vector_explosion_rect.center = (self.ship.position.x, self.ship.position.y)
            self.worldsurf.blit(self.vector_explosion, self.vector_explosion_rect)
        if self.bonus_exists:
            if self.bonus.visible:
                self.bonus.draw(self.worldsurf)
        self.screen.blit(self.scoresurf, self.scorerect)
        self.screen.blit(self.worldsurf, self.worldrect)
        pygame.display.flip()
        
g = Game()
g.setup_world()

while True:
    g.clock.tick(30)
    g.process_input()
    g.process_game_logic()
    g.process_events()              
    g.draw()
    if g.ship.alive == False:
        g.reset_position()