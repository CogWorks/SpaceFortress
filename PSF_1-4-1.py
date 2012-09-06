#PSF.py
#Version 1.4.1 - Log mine onsets, records first or second bonus symbol
#Version 1.4 - Model hooks
#Version 1.3 - config file, os dependent pathing (py2app nests the CWD three levels in)
#Version 1.2 - ship doesn't reset, more aggressive fortress, faster mines, faster ship turning
#Pygame Space Fortress
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2008

from __future__ import division
import sf_object
import score
import frame
import pygame
import sounds
import bonus
import os
import math
import time
import datetime
import sys
import thread
from timer import Timer as clock_timer
from timer_by_frame import Timer as frame_timer
import dbus #installed through Macports with custom Portfile to deal with wonky patching
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop #threaded mainloop that listens for D-Bus events
import gobject
#from eeg import *
release_build = False

pygame.init()

class World(object):
    """Main game application"""
    
    def __init__(self):
        super(World, self).__init__()
        if sys.platform == "darwin" and release_build:
            self.app_path = '../../../'
        else:
            self.app_path = '.'
        self.datapath = os.path.join(self.app_path, "data/")
        self.config = {}
        configfile = open(os.path.join(self.app_path, "config.txt"))
        configlog = configfile.readlines()
        for line in configlog:
            if line[0] in ["#", "\n"]:
                pass
            else:
                command = line.split()
                if len(command) > 2:
                    self.config[command[0]] = command[1:]
                else:
                    self.config[command[0]] = command[1]
        configfile.close()
        #print self.config
        #if human, clock-based timing. If model, frame-based timing
        global Timer
        if self.config["act-r"] == "t":
            Timer = frame_timer #why isn't this accessible outside?
        else:
            Timer = clock_timer
        self.thrust_key = eval("pygame.K_%s"%self.config["thrust_key"])
        self.left_turn_key = eval("pygame.K_%s"%self.config["left_turn_key"])
        self.right_turn_key = eval("pygame.K_%s"%self.config["right_turn_key"])
        self.fire_key = eval("pygame.K_%s"%self.config["fire_key"])
        self.IFF_key = eval("pygame.K_%s"%self.config["IFF_key"])
        self.shots_key = eval("pygame.K_%s"%self.config["shots_key"])
        self.pnts_key = eval("pygame.K_%s"%self.config["pnts_key"])
        self.SCREEN_WIDTH = 1024
        self.SCREEN_HEIGHT = 768
        self.WORLD_WIDTH = 710
        self.WORLD_HEIGHT = 626
        self.f = pygame.font.Font("fonts/freesansbold.ttf", 14)
        self.f24 = pygame.font.Font("fonts/freesansbold.ttf", 20)
        self.f96 = pygame.font.Font("fonts/freesansbold.ttf", 72)
        self.f36 = pygame.font.Font("fonts/freesansbold.ttf", 36)
        self.sounds = sounds.Sounds()
        self.bonus = bonus.Bonus()
        self.bonus.probability = float(self.config["bonus_probability"])
        self.bonus.bonus_symbol = self.config["bonus_symbol"]
        self.bonus.symbols = self.config["non_bonus_symbols"]
        #use pygame.display.list_modes() to get a sorted list of tuples. First in the list is maximum fullscreen.
        #use this to set scales appropriately
        if self.config["fullscreen"] == "f":
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        else:
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), \
            pygame.FULLSCREEN)
        #setting icon immediately after setting display mode
        pygame.display.set_icon(pygame.image.load("gfx/psficon.png").convert_alpha())
        pygame.mouse.set_visible(False)
        self.frames_per_second = 30 #not tested for anything other than 30. Recommend leaving this alone
        self.game_frame = 0
        self.keys_held = [False, False, False, False, False, False, False]

    
    def setup_world(self):
        """resets world for next 5-minute session"""
        self.shell_list = []
        self.missile_list = []
        self.clock = pygame.time.Clock()
        self.worldsurf = pygame.Surface((self.WORLD_WIDTH, self.WORLD_HEIGHT))
        self.worldrect = self.worldsurf.get_rect()
        self.worldrect.top = 5
        self.worldrect.centerx = self.SCREEN_WIDTH/2
        self.scoresurf = pygame.Surface((self.WORLD_WIDTH, 64))
        self.scorerect = self.scoresurf.get_rect()
        self.scorerect.top = 634
        self.scorerect.centerx = self.SCREEN_WIDTH/2
        self.gameover = False
        self.fortress = sf_object.fortress.Fortress(self)
        self.fortress.sector_size = int(self.config["fortress_sector_size"])
        self.fortress.lock_time = int(self.config["fortress_lock_time"])
        self.ship = sf_object.ship.Ship(self)
        self.ship.turn_speed = int(self.config["ship_turn_speed"])
        self.ship.max_vel = int(self.config["ship_max_vel"])
        self.ship.acceleration_factor = float(self.config["ship_acceleration"])
        self.ship.health = int(self.config["ship_hit_points"])
        self.score = score.Score(self)
        self.frame = frame.Frame(self)
        self.bighex = sf_object.hexagon.Hex(self, int(self.config["big_hex"]))
        self.smallhex = sf_object.hexagon.Hex(self,int(self.config["small_hex"]))
        self.mine = sf_object.mine.Mine(self)
        if self.config["mine_exists"] == "f":
            self.mine.exists = False
        self.mine.generate_foes(int(self.config["num_foes"]))
        self.mine.speed = int(self.config["mine_speed"])
        self.mine.foe_probability = float(self.config["mine_probability"])
        self.mine.reset_time = int(self.config["mine_spawn"])
        self.mine.timeout = int(self.config["mine_timeout"]) + self.mine.reset_time
        self.vector_explosion = pygame.image.load("gfx/exp.png")
        self.vector_explosion.set_colorkey((0, 0, 0))
        self.vector_explosion_rect = self.vector_explosion.get_rect()
        self.minetimer = Timer(self)
        self.fortresstimer = Timer(self)
        self.fortressdeathtimer = Timer(self)
        self.intervaltimer = Timer(self)
        self.intervalflag = False
        self.updatetimer = Timer(self)
        self.bonustimer = Timer(self)
	self.ship_death_timer = Timer(self)
        self.ship_death_flag = False
        self.bonus.flag = True
    
    def display_foe_mines(self):
        """before game begins, present the list of IFF letters to target"""
        self.screen.fill((0,0,0))
        top = self.f24.render("The FOE mines for this session are:", True, (255,255,0))
        top_rect = top.get_rect()
        top_rect.centerx = self.SCREEN_WIDTH/2
        top_rect.centery = 270
        middle = self.f96.render(", ".join(self.mine.foe_letters), True, (255,255,255))
        middle_rect = middle.get_rect()
        middle_rect.centerx = self.SCREEN_WIDTH/2
        middle_rect.centery =self.SCREEN_HEIGHT/2
        midbot = self.f24.render("Try to memorize them before proceeding", True, (255,255,0))
        midbot_rect = midbot.get_rect()
        midbot_rect.centerx = self.SCREEN_WIDTH/2
        midbot_rect.centery = 500
        bottom = self.f24.render("Press any key to begin", True, (255,255,0))
        bottom_rect = bottom.get_rect()
        bottom_rect.centerx = self.SCREEN_WIDTH/2
        bottom_rect.centery = 600
        self.screen.blit(top, top_rect)
        self.screen.blit(middle, middle_rect)
        self.screen.blit(midbot, midbot_rect)
        self.screen.blit(bottom, bottom_rect)
        pygame.display.flip()
        self.log.write("# %f %d Foe mines: %s\n"%(time.time(), pygame.time.get_ticks(), " ".join(self.mine.foe_letters)))
        
    
    def process_input_events(self):
        """chief function to process keyboard events"""
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and self.ship.alive: #don't accept key during second while ship is dead
                if event.key == pygame.K_ESCAPE:
                    self.log.write("# Escaped prematurely\n")
                    self.log.close()
                    os.rename(os.path.join(self.datapath, "%s-%d-%d.dat"%(self.config["id"], self.session_number, self.game_number)), \
                        os.path.join(self.datapath, "short-%s-%d-%d.dat"%(self.config["id"], self.session_number, self.game_number)))
                    sys.exit()
                if event.key == self.right_turn_key:
                    self.ship.turn_flag = 'right'
                    self.log.write("# start right turn\n")
                if event.key == self.left_turn_key:
                    self.ship.turn_flag = 'left'
                    self.log.write("# start left turn\n")
                if event.key == self.thrust_key:
                    self.ship.thrust_flag = True
                    self.log.write("# start thrust\n")
                if event.key == self.fire_key:
                    self.missile_list.append(sf_object.missile.Missile(self))
                    self.log.write("# fire missile\n")
                    self.sounds.missile_fired.play()
                    if self.score.shots > 0:
                        self.score.shots -= 1
                    else:
                        self.score.pnts -= int(self.config["missile_penalty"])
                if event.key == self.IFF_key:
                    self.log.write("# press IFF key\n")
                    if self.intervalflag == False:
                        self.intervaltimer.reset()
                        self.intervalflag = True
                    else:
                        self.score.intrvl = self.intervaltimer.elapsed()
                        self.intervalflag = False
                if event.key == self.shots_key:
                    self.log.write("# press shots key\n")
                    if self.bonus.current_symbol == self.bonus.bonus_symbol and self.bonus.prior_symbol == self.bonus.bonus_symbol and self.bonus.flag:
                        self.bonus.current_symbol = "Bonus"
                        self.score.shots += 50
                        if self.score.shots > 100:
                            self.score.shots = 100
                    elif self.bonus.current_symbol == self.bonus.bonus_symbol and self.bonus.prior_symbol != self.bonus.bonus_symbol:
                        self.bonus.flag = False
                if event.key == self.pnts_key:
                    self.log.write("# press points key\n")
                    if self.bonus.current_symbol == self.bonus.bonus_symbol and self.bonus.prior_symbol == self.bonus.bonus_symbol and self.bonus.flag:
                        self.bonus.current_symbol = "Bonus"
                        self.score.pnts += 100
                    elif self.bonus.current_symbol == self.bonus.bonus_symbol and self.bonus.prior_symbol != self.bonus.bonus_symbol:
                        self.bonus.flag = False
            if event.type == pygame.KEYUP:
                if event.key == self.left_turn_key:
                    self.log.write("# end left turn\n")
                    self.ship.turn_flag = False
                if event.key == self.right_turn_key:
                    self.log.write("# end right turn\n")
                    self.ship.turn_flag = False
                if event.key == self.thrust_key:
                    self.log.write("# end thrust\n")
                    self.ship.thrust_flag = False
                if event.key == self.fire_key:
                    self.log.write("# release fire key\n")
                if event.key == self.IFF_key:
                    self.log.write("# release IFF key\n")
                if event.key == self.shots_key:
                    self.log.write("# release shots key\n")
                if event.key == self.pnts_key:
                    self.log.write("# release points key\n")
                


    
    def update_world(self):
        """chief function to update the gameworld"""
        self.game_frame += 1
        if self.intervaltimer.elapsed() > 5000:
            self.score.intrvl = 0
            self.intervalflag = False
        if self.updatetimer.elapsed() > int(self.config["update_timer"]):
            self.updatetimer.reset()
            if (self.ship.velocity.x **2 + self.ship.velocity.y **2)**0.5 < int(self.config["speed_threshold"]):
                self.score.vlcty += int(self.config["VLCTY_increment"])
            else:
                self.score.vlcty -= int(self.config["VLCTY_increment"])
            if self.bighex.collide(self.ship):
                self.score.cntrl += int(self.config["CNTRL_increment"])
            else:
                self.score.cntrl += int(self.config["CNTRL_increment"])/2
        if self.fortressdeathtimer.elapsed() > 1000:
            self.fortress.alive = True
        self.ship.compute()                                  #move ship
        if self.smallhex.collide(self.ship):
            if self.ship.small_hex_flag == False: #if ship hits small hex, bounce it back and subtract 5 points
                self.log.write("# hit small hex\n")
                self.ship.small_hex_flag = True
                self.ship.velocity.x = -self.ship.velocity.x
                self.ship.velocity.y = -self.ship.velocity.y
                self.score.pnts -= int(self.config["small_hex_penalty"])
        else:
            self.ship.small_hex_flag = False
        self.fortress.compute(self)                     #point fortress at ship, will fire if still for a short time
        minetimer = self.minetimer.elapsed()
        if minetimer > self.mine.reset_time and self.mine.exists and self.mine.alive == False:
            self.mine.reset()
            if self.score.iff in self.mine.letters: #list that's not foe_letters
                self.log.write("# mine onset %s friend\n"%self.score.iff)
            else:
                self.log.write("# mine onset %s foe\n"%self.score.iff)
        if minetimer > self.mine.timeout and self.mine.exists:
            self.log.write("# mine timed out\n")
            self.mine.alive = False
            self.score.iff = ""
            self.score.speed -= int(self.config["mine_timeout_penalty"])
            self.minetimer.reset()
        if self.mine.alive == True:
            self.mine.compute()                                  #move mine, test to see if it hits ship
            if self.mine.test_collision(self.ship):
                self.log.write("# mine hit ship\n")
                self.ship.take_damage()
                if not self.ship.alive:
                    self.log.write("# ship destroyed\n")
                self.mine.alive = False
                self.minetimer.reset()
                self.score.pnts -= int(self.config["mine_hit_penalty"])
                self.score.iff = ""
        for i, shell in enumerate(self.shell_list):          #move any shells, delete if offscreen, tests for collision with ship
            shell.compute()
            if shell.position.x < 0 or shell.position.x > self.WORLD_WIDTH or shell.position.y < 0 or shell.position.y > self.WORLD_HEIGHT:
                del self.shell_list[i]
            if self.ship.alive:
                if shell.test_collision(self.ship):
                    self.log.write("# shell hit ship\n")
                    del self.shell_list[i]
                    self.score.pnts -= int(self.config["shell_hit_penalty"])
                    self.ship.take_damage()
                    if not self.ship.alive:
                        self.log.write("# ship destroyed\n")
        for i, missile in enumerate(self.missile_list):      #move any missiles, delete if offscreen
            missile.compute()
            if missile.position.x < 0 or missile.position.x > self.WORLD_WIDTH or missile.position.y < 0 or missile.position.y > self.WORLD_HEIGHT:
                del self.missile_list[i]
            if missile.test_collision(self.mine) and self.mine.alive: #missile hits mine?
                if self.score.iff in self.mine.letters: #friendly
                    if self.intervalflag or int(self.config["intrvl_min"]) <= self.score.intrvl <= int(self.config["intrvl_max"]): #false tag
                        self.log.write("# hit falsely tagged friend mine\n")
                        del self.missile_list[i]
                    else:
                        self.log.write("# hit friendly mine\n")
                        self.mine.alive = False
                        self.score.iff = ""
                        self.score.pnts += int(self.config["energize_friend"])
                        self.score.vlner += 1
                        #see how long mine has been alive. 0-100 points if destroyed within 10 seconds, but timer runs for 5 seconds before mine appears
                        self.score.speed += 100 - 10 * (math.floor(minetimer/1000) - 5)
                        self.minetimer.reset()
                        del self.missile_list[i]
                elif self.score.iff in self.mine.foe_letters and int(self.config["intrvl_min"]) <= self.score.intrvl <= int(self.config["intrvl_max"]): #tagged successfully? int value of "" is high
                    self.log.write("# hit tagged foe mine\n")
                    self.mine.alive = False
                    self.score.iff = ""
                    self.score.pnts += int(self.config["destroy_foe"])
                    #see how long mine has been alive. 0-100 points if destroyed within 10 seconds
                    self.score.speed += 100 - 10 * (math.floor(minetimer/1000) - 5)
                    self.minetimer.reset()
                    del self.missile_list[i]
                else: #foe mine not tagged
                    self.log.write("# hit untagged foe mine\n")
                    del self.missile_list[i]
        for i, missile in enumerate(self.missile_list):#enumerating a second time, so that when mine and fortress overlap, we only remove the missile once
            if missile.test_collision(self.fortress) and self.fortress.alive: #missile hits fortress? mine needs to be dead to hurt it
                del self.missile_list[i]
                self.log.write("# hit fortress\n")
                if not self.mine.alive and self.fortresstimer.elapsed() >= int(self.config["vlner_time"]):
                    self.score.vlner += 1
                    self.log.write("# VLNER++\n")
                if not self.mine.alive and self.fortresstimer.elapsed() < int(self.config["vlner_time"]) and self.score.vlner >= (int(self.config["vlner_threshold"]) + 1):
                    self.log.write("# fortress destroyed\n")
                    self.fortress.alive = False
                    self.score.pnts += int(self.config["destroy_fortress"])
                    self.score.vlner = 0
                    self.sounds.explosion.play()
                    self.minetimer.reset()
                    self.mine.alive = False
                    self.score.iff = ""
                    self.ship.alive = True
                    self.fortressdeathtimer.reset()
                    #self.reset_position()
                if not self.mine.alive and self.fortresstimer.elapsed() < int(self.config["vlner_time"]) and self.score.vlner < (int(self.config["vlner_threshold"]) + 1):
                    self.log.write("# VLNER reset\n")
                    self.score.vlner = 0
                    self.sounds.vlner_reset.play()
                self.fortresstimer.reset()
        if (self.bonus.visible == False) and (self.bonustimer.elapsed() >= int(self.config["symbol_down_time"])): #original span is 25 frames, time for new symbol
            self.bonus.visible = True
            self.bonustimer.reset()
            self.bonus.prior_symbol = self.bonus.current_symbol
            self.bonus.get_new_symbol()
            self.log.write("# new symbol %s\n"%self.bonus.current_symbol)
            if self.bonus.prior_symbol == self.bonus.bonus_symbol and self.bonus.current_symbol == self.bonus.bonus_symbol:
                self.log.write("# second appearance of bonus symbol\n")
            if self.bonus.prior_symbol != self.bonus.bonus_symbol and self.bonus.current_symbol == self.bonus.bonus_symbol:
                self.log.write("# first appearance of bonus symbol\n")
        elif (self.bonus.visible == True) and (self.bonustimer.elapsed() >= int(self.config["symbol_up_time"])): #keep symbol visible for 75 frames
            self.bonus.visible = False
            #self.bonus.current_symbol = ''
            self.log.write("# symbol disappeared\n")
            self.bonustimer.reset()
    
    def reset_position(self):
        """pauses the game and resets"""
       	self.ship.velocity.x = 0
        self.ship.velocity.y = 0
        if self.ship_death_flag == False:
            self.sounds.explosion.play()
            self.ship_death_flag = True
            self.ship_death_timer.reset()
            self.score.pnts -= int(w.config["ship_death_penalty"])
        #    print "resetting death timer"
        if self.ship_death_flag and self.ship_death_timer.elapsed() > 1000:
            #print "reset position"
            self.ship_death_flag = False
            self.minetimer.reset()
            self.mine.alive = False
            self.score.iff = ""
            self.ship.alive = True
            self.fortress.alive = True
            self.ship.position.x = 245
            self.ship.position.y = 315
            self.ship.velocity.x = 0
            self.ship.velocity.y = 0
            self.ship.orientation = 90
    
    
    def draw_world(self):
        """chief function to draw the world"""
        self.screen.fill((0,0,0))
        self.worldsurf.fill((0,0,0))
        self.scoresurf.fill((0,0,0))
        self.frame.draw(self.worldsurf, self.scoresurf)
        for shell in self.shell_list:
            shell.draw(self.worldsurf)
        for missile in self.missile_list:
            missile.draw(self.worldsurf)
        #draws a small black circle under the fortress so we don't see the shell in the center
        pygame.draw.circle(self.worldsurf, (0,0,0), (355,315), 30)
        if self.fortress.alive:
            self.fortress.draw(self.worldsurf)
        else:
            self.vector_explosion_rect.center = (self.fortress.position.x, self.fortress.position.y)
            self.worldsurf.blit(self.vector_explosion, self.vector_explosion_rect)
        if self.ship.alive:
            self.ship.draw(self.worldsurf)
        else:
            self.vector_explosion_rect.center = (self.ship.position.x, self.ship.position.y)
            self.worldsurf.blit(self.vector_explosion, self.vector_explosion_rect)
        self.score.draw(self.scoresurf)
        self.bighex.draw(self.worldsurf)
        self.smallhex.draw(self.worldsurf)
        if self.mine.alive:
            self.mine.draw(self.worldsurf)
        if self.bonus.visible:
            self.bonus.draw(self.worldsurf)
        if self.keys_held[1]:
            self.screen.blit(self.f.render("Left", 1, (0,255,0)), (30,50))
        else:
            self.screen.blit(self.f.render("Left", 1, (0,50,0)), (30,50))
        if self.keys_held[2]:
            self.screen.blit(self.f.render("Right", 1, (0,255,0)), (30,70))
        else:
            self.screen.blit(self.f.render("Right", 1, (0,50,0)), (30,70))
        if self.keys_held[0]:
            self.screen.blit(self.f.render("Thrust", 1, (0,255,0)), (30,90))
        else:
            self.screen.blit(self.f.render("Thrust", 1, (0,50,0)), (30,90))
        if self.keys_held[6]:
            self.screen.blit(self.f.render("Fire", 1, (0,255,0)), (30,110)) 
        else:
            self.screen.blit(self.f.render("Fire", 1, (0,50,0)), (30,110)) 
        if self.keys_held[3]:
            self.screen.blit(self.f.render("IFF", 1, (0,255,0)), (30,130))
        else:
            self.screen.blit(self.f.render("IFF", 1, (0,50,0)), (30,130))
        if self.keys_held[4]:
            self.screen.blit(self.f.render("SHOTS", 1, (0,255,0)), (30,150))
        else:
            self.screen.blit(self.f.render("SHOTS", 1, (0,50,0)), (30,150))
        if self.keys_held[5]:
            self.screen.blit(self.f.render("PNTS", 1, (0,255,0)), (30,170))
        else:
            self.screen.blit(self.f.render("PNTS", 1, (0,50,0)), (30,170))
        self.screen.blit(self.worldsurf, self.worldrect)
        self.screen.blit(self.scoresurf, self.scorerect)
        
        
    
    def log_world(self):
        """log current frame's data to text file. Note that first line contains foe mine designations
        format:
        system_clock game_time ship_alive? ship_x ship_y ship_vel_x ship_vel_y ship_orientation mine_alive? mine_x mine_y 
        fortress_alive? fortress_orientation [missile_x missile_y ...] [shell_x shell_y ...] bonus_symbol
        pnts cntrl vlcty vlner iff intervl speed shots thrust_key left_key right_key fire_key iff_key shots_key pnts_key"""
        system_clock = time.time()
        game_time = pygame.time.get_ticks()
        if self.ship.alive:
            ship_alive = "y"
            ship_x = "%.3f"%(self.ship.position.x)
            ship_y = "%.3f"%(self.ship.position.y)
            ship_vel_x = "%.3f"%(self.ship.velocity.x)
            ship_vel_y = "%.3f"%(self.ship.velocity.y)
            ship_orientation = "%.3f"%(self.ship.orientation)
        else:
            ship_alive = "n"
            ship_x = "-"
            ship_y = "-"
            ship_vel_x = "-"
            ship_vel_y = "-"
            ship_orientation = "-"
        if self.mine.alive:
            mine_alive = "y"
            mine_x = "%.3f"%(self.mine.position.x)
            mine_y = "%.3f"%(self.mine.position.y)
        else:
            mine_alive = "n"
            mine_x = "-"
            mine_y = "-"
        if self.fortress.alive:
            fortress_alive = "y"
            fortress_orientation = str(self.fortress.orientation)
        else:
            fortress_alive = "n"
            fortress_orientation = "-"
        missile = '['
        for m in self.missile_list:
            missile += "%.3f %.3f "%(m.position.x, m.position.y)
        missile += ']'
        shell = '['
        for s in self.shell_list:
            shell += "%.3f %.3f "%(s.position.x, s.position.y)
        shell += ']'
        if self.bonus.current_symbol == '':
            bonus = "-"
        else:
            bonus = self.bonus.current_symbol
        keys = pygame.key.get_pressed()
        if keys[self.thrust_key]:
            thrust_key = "y"
        else:
            thrust_key = "n"
        if keys[self.left_turn_key]:
            left_key = "y"
        else:
            left_key = "n"
        if keys[self.right_turn_key]:
            right_key = "y"
        else:
            right_key = "n"
        if keys[self.fire_key]:
            fire_key = "y"
        else:
            fire_key = "n"
        if keys[self.IFF_key]:
            iff_key = "y"
        else:
            iff_key = "n"
        if keys[self.shots_key]:
            shots_key = "y"
        else:
            shots_key = "n"
        if keys[self.pnts_key]:
            pnts_key = "y"
        else:
            pnts_key = "n"
        self.log.write("%f %d %s %s %s %s %s %s %s %s %s %s %s %s %s %s %d %d %d %d %s %d %d %d %s %s %s %s %s %s %s\n"%\
        (system_clock, game_time, ship_alive, ship_x, ship_y, ship_vel_x, ship_vel_y, ship_orientation, mine_alive, mine_x, mine_y, fortress_alive, fortress_orientation,\
        missile, shell, bonus, self.score.pnts, self.score.cntrl, self.score.vlcty, self.score.vlner, self.score.iff, self.score.intrvl,\
        self.score.speed, self.score.shots, thrust_key, left_key, right_key, fire_key, iff_key, shots_key, pnts_key))
    
    def find_session(self):
        """method to determine which session file to open next"""
        if not os.path.exists(self.datapath):
            os.mkdir(self.datapath)
        subject_id = self.config["id"]
        self.session_number = 1
        self.game_number = 1
        while True:
            tempname = os.path.join(self.datapath, "%s-%d-%d.dat"%(subject_id, self.session_number, self.game_number))
            #print tempname
            if os.path.exists(tempname):
                if self.game_number == int(self.config["games_per_session"]):
                    self.game_number = 1
                    self.session_number +=1
                else:
                    self.game_number += 1
            else: #We're at the first file that doesn't exist. Need to check if *prior* game ended prematurely
                if not (self.session_number == 1 and self.game_number == 1): #is there a prior version at all?
                    if self.game_number == 1: #need last game of previous session
                        prior_game = int(self.config["games_per_session"])
                        prior_session = self.session_number - 1
                    else:
                        prior_game = self.game_number - 1
                        prior_session = self.session_number
                    #check priors for last line
                    lastname = os.path.join(self.datapath, "%s-%d-%d.dat"%(subject_id, prior_session, prior_game))
                    lastfile = open(lastname).readlines()
                    if lastfile[-1].split()[1] == "Escaped": #last game played ended prematurely!
                        os.rename(lastname, os.path.join(self.datapath, "short-%s-%d-%d.dat"%(subject_id, prior_session, prior_game)))
                        tempname = lastname
                        self.game_number = prior_game
                        self.session_number = prior_session
                self.log = open(tempname, "w")
                self.log.write("# log version 1.4\n")
                self.log.write("# non-hashed line notation:\n")
                self.log.write("# system_clock game_time ship_alive? ship_x ship_y ship_vel_x ship_vel_y ship_orientation mine_alive? mine_x mine_y \
fortress_alive? fortress_orientation [missile_x missile_y ...] [shell_x shell_y ...] bonus_symbol \
pnts cntrl vlcty vlner iff intervl speed shots thrust_key left_key right_key fire_key iff_key shots_key pnts_key\n")
                return
    
    def fade(self):
        """fade screen to show score"""
        fadesurf = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT)).convert_alpha()
        fadesurf.fill((0,0,0,6))
        for i in range(100):
            self.screen.blit(fadesurf, pygame.Rect(0,0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            pygame.display.flip()
    
    def show_score(self):
        """shows score for last game and waits to continue"""
        pygame.event.get() #clear event list? Otherwise it skips
        self.screen.fill((0, 0, 0))
        sessionsurf = self.f24.render("Session %d, Game %d/%s"%(self.session_number, self.game_number, self.config["games_per_session"]), True, (255,255,255))
        sessionrect = sessionsurf.get_rect()
        sessionrect.centerx = self.SCREEN_WIDTH / 2
        sessionrect.y = 100
        self.screen.blit(sessionsurf, sessionrect)
        pntssurf = self.f24.render("PNTS score:", True, (255, 255,0))
        pntsrect = pntssurf.get_rect()
        pntsrect.move_ip((250, 200))
        self.screen.blit(pntssurf, pntsrect)
        cntrlsurf = self.f24.render("CNTRL score:", True, (255, 255,0))
        cntrlrect = cntrlsurf.get_rect()
        cntrlrect.move_ip((250, 300))
        self.screen.blit(cntrlsurf, cntrlrect)
        vlctysurf = self.f24.render("VLCTY score:", True, (255, 255,0))
        vlctyrect = vlctysurf.get_rect()
        vlctyrect.move_ip((250, 400))
        self.screen.blit(vlctysurf, vlctyrect)
        speedsurf = self.f24.render("SPEED score:", True, (255, 255,0))
        speedrect = speedsurf.get_rect()
        speedrect.move_ip((250, 500))
        self.screen.blit(speedsurf, speedrect)
        pntsnsurf = self.f24.render("%d"%self.score.pnts, True, (255, 255,255))
        pntsnrect = pntsnsurf.get_rect()
        pntsnrect.right = 700
        pntsnrect.y = 200
        self.screen.blit(pntsnsurf, pntsnrect)
        cntrlnsurf = self.f24.render("%d"%self.score.cntrl, True, (255, 255,255))
        cntrlnrect = cntrlnsurf.get_rect()
        cntrlnrect.right = 700
        cntrlnrect.y = 300
        self.screen.blit(cntrlnsurf, cntrlnrect)
        vlctynsurf = self.f24.render("%d"%self.score.vlcty, True, (255, 255,255))
        vlctynrect = vlctynsurf.get_rect()
        vlctynrect.right = 700
        vlctynrect.y = 400
        self.screen.blit(vlctynsurf, vlctynrect)
        speednsurf = self.f24.render("%d"%self.score.speed, True, (255, 255,255))
        speednrect = speednsurf.get_rect()
        speednrect.right = 700
        speednrect.y = 500
        self.screen.blit(speednsurf, speednrect)
        #draw line
        pygame.draw.line(self.screen, (255, 255, 255), (200, 580), (800, 580))
        totalsurf = self.f24.render("Total score for this game:", True, (255, 255,0))
        totalrect = totalsurf.get_rect()
        totalrect.move_ip((200, 620))
        self.screen.blit(totalsurf, totalrect)
        totalnsurf = self.f24.render("%d"%(self.score.pnts + self.score.cntrl + self.score.vlcty + self.score.speed), True, (255, 255,255))
        totalnrect = totalnsurf.get_rect()
        totalnrect.right = 700
        totalnrect.y = 620
        self.screen.blit(totalnsurf, totalnrect)
        if self.game_number == int(self.config["games_per_session"]):
            finalsurf = self.f24.render("You're done! Press any key to exit", True, (0,255,0))
        else:
            finalsurf = self.f24.render("Press any key to continue to next game or ESC to exit", True, (255,255,255))
        finalrect = finalsurf.get_rect()
        finalrect.centerx = self.SCREEN_WIDTH /2
        finalrect.y = 700
        self.screen.blit(finalsurf, finalrect)
        pygame.display.flip()
        self.log.write("# pnts score %d\n"%self.score.pnts)
        self.log.write("# cntrl score %d\n"%self.score.cntrl)
        self.log.write("# vlcty score %d\n"%self.score.vlcty)
        self.log.write("# speed score %d\n"%self.score.speed)
        self.log.write("# total score %d"%(self.score.pnts + self.score.cntrl + self.score.vlcty + self.score.speed))
        self.log.close()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                    else:
                        return
    

class DBus_obj(dbus.service.Object):
      
    @dbus.service.method("edu.rpi.cogsci.destem.Interface", in_signature='s', out_signature='s')
    def test(self, hello_message):
        print "Got the message \'%s\'"%hello_message
        return "I received your kind message that said \'%s\'"%hello_message
    
    @dbus.service.method("edu.rpi.cogsci.destem.Interface", in_signature='s', out_signature='s')
    def exit_game(self, blank):
        os._exit(0)
    
    @dbus.service.method("edu.rpi.cogsci.destem.Interface", in_signature='s', out_signature='s')
    def begin(self, input_string):
        self.w.log = open("testing.dat", "w")
        self.w.setup_world()
        self.w.display_foe_mines()
        return "(%s %s %s)"%(self.w.mine.foe_letters[0], self.w.mine.foe_letters[1], self.w.mine.foe_letters[2])
    
    @dbus.service.method("edu.rpi.cogsci.destem.Interface", in_signature='s', out_signature='s')
    def reset_timers(self, input_string):      
        self.w.minetimer.reset()
        self.w.updatetimer.reset()
        self.w.bonustimer.reset()
        return "Timers reset"

    @dbus.service.method("edu.rpi.cogsci.destem.Interface", in_signature='s', out_signature='s')
    def reset_all(self, blank):  
        self.w.setup_world()    
        self.w.minetimer.reset()
        self.w.updatetimer.reset()
        self.w.bonustimer.reset()
        self.w.draw_world()
        pygame.display.flip()
        return "game reset"
    
    @dbus.service.method("edu.rpi.cogsci.destem.Interface", in_signature='s', out_signature='s')
    def send_pound(self, input_string):
        return ("(#)")
    
    @dbus.service.method("edu.rpi.cogsci.destem.Interface", in_signature='s', out_signature='s')
    def update_world(self, blank):
        self.w.update_world()
        #format: ship-exist? shipx shipy ship_velx, ship_vely, shipangle fortress-exist? fortress-angle mine-exist? minex miney
        #shell-exist? shellx shelly bonus-exist? bonus-symbol PNTS CNTRL VLCTY VLNER IFF INTRVL SPEED SHOTS
        if w.ship.alive:
            s_e = "y"
        else:
            s_e = "n"
        if w.fortress.alive:
            f_e = "y"
        else:
            f_e = "n"
        if w.mine.alive:
            m_e = "y"
        else:
            m_e = "n"
        if len(w.shell_list) == 0:
            sh_e = "n"
            sh_x = 0
            sh_y = 0
        else:
            sh_e = "y"
            sh_x = w.shell_list[0].position.x + 157
            sh_y = w.shell_list[0].position.y + 5
        if w.bonus.visible:
            b_e = "y"
        else:
            b_e = "n"
        if w.bonus.current_symbol == "":
            b_cs = '-'
        else:
            b_cs = w.bonus.current_symbol
        if w.score.iff == "":
            iff = "-"
        else:
            iff = w.score.iff

        #print  "(%s %f %f %f %f %d %s %d %s %f %f %s %f %f %s %s %d %d %d %d %s %s %s %s)"\
        #%(s_e, w.ship.position.x + 157, w.ship.position.y + 5, w.ship.velocity.x, w.ship.velocity.y, w.ship.orientation, f_e, w.fortress.orientation, \
        #m_e, w.mine.position.x + 157, w.mine.position.y + 5, sh_e, sh_x, sh_y, b_e, b_cs, \
        #w.score.pnts, w.score.cntrl, w.score.vlcty, w.score.vlner, iff, w.score.intrvl, w.score.speed, w.score.shots)
            
        return "(%s %f %f %f %f %d %s %d %s %f %f %s %f %f %s %s %d %d %d %d %s %s %s %s)"\
        %(s_e, w.ship.position.x + 157, w.ship.position.y + 5, w.ship.velocity.x, w.ship.velocity.y, w.ship.orientation, f_e, w.fortress.orientation, \
        m_e, w.mine.position.x + 157, w.mine.position.y + 5, sh_e, sh_x, sh_y, b_e, b_cs, \
        w.score.pnts, w.score.cntrl, w.score.vlcty, w.score.vlner, iff, w.score.intrvl, w.score.speed, w.score.shots)
        #sending positions in screen coordinates because model needs to look outside "world" view
    
    @dbus.service.method("edu.rpi.cogsci.destem.Interface", in_signature='s', out_signature='s')
    def press_key(self, key):
        """Adds pygame event to queue"""
        if key=="return":
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key":pygame.K_RETURN}))
        elif key=="w":
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key":pygame.K_w}))
            self.w.keys_held[0] = True
        elif key=="a":
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key":pygame.K_a}))
            self.w.keys_held[1] = True
        elif key=="d":
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key":pygame.K_d}))
            self.w.keys_held[2] = True
        elif key=="j":
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key":pygame.K_j}))
            self.w.keys_held[3] = True
        elif key=="k":
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key":pygame.K_k}))
            self.w.keys_held[4] = True
        elif key=="l":
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key":pygame.K_l}))
            self.w.keys_held[5] = True
        elif key=="space":
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key":pygame.K_SPACE}))
            self.w.keys_held[6] = True
        return "Key pressed"
    
    @dbus.service.method("edu.rpi.cogsci.destem.Interface", in_signature='s', out_signature='s')
    def release_key(self, key):
        """Adds pygame event to queue"""
        if key=="w":
            pygame.event.post(pygame.event.Event(pygame.KEYUP, {"key":pygame.K_w}))
            self.w.keys_held[0] = False
        elif key=="a":
            pygame.event.post(pygame.event.Event(pygame.KEYUP, {"key":pygame.K_a}))
            self.w.keys_held[1] = False
        elif key=="d":
            pygame.event.post(pygame.event.Event(pygame.KEYUP, {"key":pygame.K_d}))
            self.w.keys_held[2] = False
        elif key=="j":
            self.w.keys_held[3] = False
        elif key=="k":
            self.w.keys_held[4] = False
        elif key=="l":
            self.w.keys_held[5] = False
        elif key=="space":
            self.w.keys_held[6] = False           
        return "Key released"
    

    @dbus.service.method("edu.rpi.cogsci.destem.Interface", in_signature='s', out_signature='s')
    def process_input(self, input_string):
        self.w.process_input_events()
        return "Input Processed"
    
    @dbus.service.method("edu.rpi.cogsci.destem.Interface", in_signature='s', out_signature='s')
    def draw_world(self, input_string):
        self.w.draw_world()
        #pygame.draw.circle(self.w.screen, (255,255,255), (512,320), 95, 1)
        pygame.display.flip()
        if self.w.ship.alive == False:
            self.w.reset_position()
        return "World Drawn"
    

if __name__ == '__main__':
    w = World()
    if w.config["act-r"] == 't':
        DBusGMainLoop(set_as_default=True) #must do this before connecting to the bus
        session_bus = dbus.SessionBus() #creates session bus
        name = dbus.service.BusName("edu.rpi.cogsci.destem", session_bus)
        dbus_object = DBus_obj(session_bus, '/DBus_obj')
        dbus_object.w = w
        gloop = gobject.MainLoop()
        waitmsg = w.f24.render("Waiting for ACT-R to connect", 1, (255,255,255))
        waitmsg_rect = waitmsg.get_rect()
        waitmsg_rect.center = (w.SCREEN_WIDTH/2, w.SCREEN_HEIGHT/2)
        w.screen.blit(waitmsg, waitmsg_rect)
        pygame.display.flip()
        pygame.event.set_grab(False)
        gobject.threads_init() #only necessary to capture keyboard events before ACT-R connects
        gloop.run()
    else:
        w.find_session()
        w.setup_world()
        w.display_foe_mines()
        init_setup = False
        while init_setup == False:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    init_setup = True
        w.minetimer.reset()
        w.updatetimer.reset()
        w.bonustimer.reset()
        gameTimer = Timer(w)
        while w.gameover == False:
            w.clock.tick(w.frames_per_second)
            w.process_input_events()
            w.update_world()
            w.log_world()
            w.draw_world()
            pygame.display.flip()
            if w.ship.alive == False:
                w.reset_position()
            if gameTimer.elapsed() >= int(w.config["game_time"]): #300000 milliseconds = five minutes per game
                w.fade()
                w.show_score()
                if w.game_number != int(w.config["games_per_session"]):
                    w.find_session()
                    w.setup_world()
                    w.display_foe_mines()
                    while True:
                        for event in pygame.event.get():
                            if event.type == pygame.KEYDOWN:
                                break
                    gameTimer.reset()
                    w.minetimer.reset()
                    w.updatetimer.reset()
                    w.bonustimer.reset()
                else:
                    sys.exit()
