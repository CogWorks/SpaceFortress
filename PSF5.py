#!/usr/bin/env python

from __future__ import division
import subprocess, os, sys, platform, math

githash = None
env = os.environ
env['PATH'] = '/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/usr/local/git/bin:/opt/local/bin:/opt/local/sbin'
if platform.system() == 'Windows':
    try:
        subprocess.call(['make','deps'],env=env)
    except OSError:
        pass
    except WindowsError:
        pass
else:
    try:
        subprocess.call(['make','deps'],env=env)
    except OSError:
        pass
try:
    f = open(os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), 'build-info'), 'r')
    githash = f.read()
    githash = githash[:-1]
    f.close()
except IOError:
    pass
if not githash:
    sys.exit("Must run 'make deps' before running.")
    
import tokens
from tokens.gameevent import *
import sys, os
import pygame
import picture
import time
import datetime
import defaults

def get_psf_version_string():
    return "Space Fortress 5"

def get_default_logdir():
    _home = os.environ.get('HOME', '/')
    if platform.system() == 'Windows':
        logdir = os.path.join(os.environ['USERPROFILE'], 'My Documents', 'Spacefortress')
    elif platform.system() == 'Linux' or platform.system() == 'Darwin':
        logdir = os.path.join(_home, 'Documents', 'Spacefortress')
    else:
        logdir = os.path.join(_home, 'Spacefortress')
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    return logdir

release_build = False

class Game(object):
    """Main game application"""
    def __init__(self):
        super(Game, self).__init__()
        self.current_game = 0

        i = sys.argv[0].rfind('/')
        if i != -1:
            self.approot = sys.argv[0][:sys.argv[0].rfind('/')]
        else:
            self.approot = './'

        self.gameevents = GameEventList(self)
        self.plugins = defaults.load_plugins(self, defaults.get_plugin_home())
        for name in self.plugins:
            try:
                self.gameevents.addCallback(self.plugins[name].eventCallback)
            except AttributeError:
                pass
                
        self.gameevents.add("game","version",githash)
                
        self.config = defaults.get_config()
        self.config.set_user_file(defaults.get_user_file())
        self.gameevents.add("config", "load", "defaults")
        self.config.update_from_user_file()
        self.gameevents.add("config", "load", "user")
        
        d = datetime.datetime.now().timetuple()
        base = "%s_%d-%d-%d_%d-%d-%d"%(self.config.get_setting('General','id'), d[0], d[1], d[2], d[3], d[4], d[5])
        logdir = self.config.get_setting('Logging','logdir')
        if len(logdir.strip()) == 0:
            logdir = get_default_logdir()
        self.log_basename = os.path.join(logdir, base)
        self.gameevents.add("log", "basename", "ready")
        
        if self.config.get_setting('Logging','logging'):
            log_filename = "%s.txt" % (self.log_basename)
            self.log = open(log_filename, "w")
            self.log.write("event_type\tsystem_clock\tgame_time\tcurrent_game\teid\te1\te2\te3\tfoes\tship_alive\tship_x\t"+
                           "ship_y\tship_vel_x\tship_vel_y\tship_orientation\tdistance\tmine_alive\tmine_x\tmine_y\tfortress_alive\tfortress_orientation\t"+
                           "missile\tshell\tbonus_prev\tbonus_cur\tbonus_cur_x\tbonus_cur_y\t")
            if self.config.get_setting('General','bonus_system') == "AX-CPT":
                self.log.write('bonus_isi\t')
            self.log.write("score_pnts\tscore_cntrl\tscore_vlcty\tscore_vlner\t"+
                           "score_iff\tscore_intrvl\tscore_speed\tscore_shots\tscore_flight\tscore_fortress\tscore_mine\tscore_bonus\tthrust_key\tleft_key\t"+
                           "right_key\tfire_key\tiff_key\tshots_key\tpnts_key")
            for name in self.plugins:
                try:
                    header = self.plugins[name].logHeader()
                    if header:
                        self.log.write(header)
                except AttributeError:
                    pass
            self.log.write("\n")
            self.gameevents.add("log", "header", "ready", log=False)
        
        self.gameevents.add("config","running",str(self.config))
        
        pygame.display.init()
        pygame.font.init()
        pygame.mouse.set_visible(False)
        display_info = pygame.display.Info()
        mode_list = pygame.display.list_modes()
        if self.config.get_setting('Display','display_mode') == 'Windowed':
            best_mode = mode_list[1]
        else:
            best_mode = mode_list[0]
        self.SCREEN_WIDTH = best_mode[0]
        self.SCREEN_HEIGHT = best_mode[1]
        self.set_aspect_ratio()
        os.environ['SDL_VIDEO_WINDOW_POS'] = str(int(mode_list[0][0]/2-self.SCREEN_WIDTH/2)) + "," + str(int(mode_list[0][1]/2-self.SCREEN_HEIGHT/2))
        self.WORLD_WIDTH = int(710 * self.aspect_ratio)
        self.WORLD_HEIGHT = int(626 * self.aspect_ratio)
        self.linewidth = self.config.get_setting('Display','linewidth')
        
        self.fp = os.path.join(self.approot, "fonts/freesansbold.ttf")
        self.f = pygame.font.Font(self.fp, int(14*self.aspect_ratio))
        self.f24 = pygame.font.Font(self.fp, int(20*self.aspect_ratio))
        self.f28 = pygame.font.Font(self.fp, int(28*self.aspect_ratio))
        self.f96 = pygame.font.Font(self.fp, int(72*self.aspect_ratio))
        self.f36 = pygame.font.Font(self.fp, int(36*self.aspect_ratio))
        
        self.frame = tokens.frame.Frame(self)
        self.gameevents.add("score1",self.frame.p1_rect.centerx,self.frame.p1_rect.centery)
        self.gameevents.add("score2",self.frame.p2_rect.centerx,self.frame.p2_rect.centery)
        self.gameevents.add("score3",self.frame.p3_rect.centerx,self.frame.p3_rect.centery)
        self.gameevents.add("score4",self.frame.p4_rect.centerx,self.frame.p4_rect.centery)
        self.gameevents.add("score5",self.frame.p5_rect.centerx,self.frame.p5_rect.centery)
        self.gameevents.add("score6",self.frame.p6_rect.centerx,self.frame.p6_rect.centery)
        self.gameevents.add("score7",self.frame.p7_rect.centerx,self.frame.p7_rect.centery)
        self.gameevents.add("score8",self.frame.p8_rect.centerx,self.frame.p8_rect.centery)

        self.score = tokens.score.Score(self)
        
        self.joystick = None
        if self.config.get_setting('Joystick','use_joystick'):
            pygame.joystick.init()
            self.joystick = pygame.joystick.Joystick(self.config.get_setting('Joystick','joystick_id'))
            self.joystick.init()
            self.fire_button = self.config.get_setting('Joystick','fire_button')
            self.IFF_button = self.config.get_setting('Joystick','iff_button')
            self.shots_button = self.config.get_setting('Joystick','shots_button')
            self.pnts_button = self.config.get_setting('Joystick','pnts_button')
            
        self.thrust_key = eval("pygame.K_%s" % self.config.get_setting('Keybindings','thrust_key'))
        self.left_turn_key = eval("pygame.K_%s" % self.config.get_setting('Keybindings','left_turn_key'))
        self.right_turn_key = eval("pygame.K_%s" % self.config.get_setting('Keybindings','right_turn_key'))
        self.fire_key = eval("pygame.K_%s" % self.config.get_setting('Keybindings','fire_key'))
        self.IFF_key = eval("pygame.K_%s" % self.config.get_setting('Keybindings','IFF_key'))
        self.shots_key = eval("pygame.K_%s" % self.config.get_setting('Keybindings','shots_key'))
        self.pnts_key = eval("pygame.K_%s" % self.config.get_setting('Keybindings','pnts_key'))
            
        self.pause_key = eval("pygame.K_%s" % self.config.get_setting('Keybindings','pause_key'))
        
        self.vector_explosion = pygame.image.load(os.path.join(self.approot, "gfx/exp.png"))
        self.vector_explosion.set_colorkey((0, 0, 0))
        self.vector_explosion_rect = self.vector_explosion.get_rect()
        self.sounds = tokens.sounds.Sounds(self)
        if self.config.get_setting('Display','display_mode') == 'Fullscreen':
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.FULLSCREEN)
        elif self.config.get_setting('Display','display_mode') == 'Fake Fullscreen':
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.NOFRAME)
        else:
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        
        self.gameevents.add("display", 'setmode', (self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.aspect_ratio))
            
        self.clock = pygame.time.Clock()
        self.gametimer = tokens.timer.Timer()
        self.flighttimer = tokens.timer.Timer()
        self.worldsurf = pygame.Surface((self.WORLD_WIDTH, self.WORLD_HEIGHT))
        self.worldrect = self.worldsurf.get_rect()
        self.worldrect.centerx = self.SCREEN_WIDTH/2
        self.worldrect.centery = self.SCREEN_HEIGHT/2
        if not self.config.get_setting('Score','new_scoring_pos'):
            self.worldrect.top = 5 * self.aspect_ratio
            self.scoresurf = pygame.Surface((self.WORLD_WIDTH, 64*self.aspect_ratio))
            self.scorerect = self.scoresurf.get_rect()
            self.scorerect.top = 634 * self.aspect_ratio
            self.scorerect.centerx = self.SCREEN_WIDTH/2
        else:
            self.worldrect.top = 70 * self.aspect_ratio
            self.scoresurf = pygame.Surface.copy(self.screen)
            self.scorerect = self.screen.get_rect()
            #self.scorerect.top = 5
        self.bighex = tokens.hexagon.Hex(self, self.config.get_setting('Hexagon','big_hex'))
        if self.config.get_setting('Hexagon','hide_big_hex'):
            self.bighex.color = (0,0,0)
        self.smallhex = tokens.hexagon.Hex(self, self.config.get_setting('Hexagon','small_hex'))
        if self.config.get_setting('Hexagon','hide_small_hex'):
            self.smallhex.color = (0,0,0) 
        if self.config.get_setting('Mine','mine_exists'):
            self.mine_exists = True
        else:
            self.mine_exists = False
        self.mine_list = tokens.mine.MineList(self)
    
    def set_aspect_ratio(self):
        self.aspect_ratio = self.SCREEN_HEIGHT/768
        xover = self.SCREEN_WIDTH + 2 * (495 * self.aspect_ratio - self.SCREEN_WIDTH / 2)
        if xover > self.SCREEN_WIDTH:
            self.aspect_ratio = self.SCREEN_WIDTH / 1024
    
    def setup_world(self):
        """initializes gameplay"""
        self.gameevents.add("game", "setup")
        self.missile_list = []
        self.shell_list = []
        self.ship = tokens.ship.Ship(self)
        if self.config.get_setting('Bonus','bonus_exists'):
            self.bonus = tokens.bonus.Bonus(self)
            self.bonus_exists = True
        else:
            self.bonus_exists = False
        if self.config.get_setting('Fortress','fortress_exists'):
            self.fortress = tokens.fortress.Fortress(self)
            self.fortress_exists = True
        else:
            self.fortress_exists = False
        self.score.pnts = 0
        self.score.cntrl = 0
        self.score.vlcty = 0
        self.score.speed = 0
        self.score.flight = 0
        self.score.fortress = 0
        self.score.mines = 0
        self.score.bonus = 0
        self.score.vlner = 0
        self.score.shots = self.config.get_setting('Missile','missile_num')        
        self.gametimer.reset()
        self.flighttimer.reset()
        self.mine_list.timer.reset()
        self.mine_list.MOT_timer.reset()
        self.mine_list.MOT_switch_timer.reset()
        
    def pause_game(self):
        """pause game till player is ready to resume"""
        if self.config.get_setting('Display','pause_overlay'):
            backup = self.screen.copy()
            self.screen.fill((0,0,0))
            pause = self.f96.render("Paused!", True, (255,255,255))
            pause_rect = pause.get_rect()
            pause_rect.centerx = self.SCREEN_WIDTH/2
            pause_rect.centery =self.SCREEN_HEIGHT/2
            self.screen.blit(pause, pause_rect)
            pygame.display.flip()
        while True:
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN and event.key == self.pause_key:
                self.gameevents.add("press", "unpause")
                if self.config.get_setting('Display','pause_overlay'):
                    self.screen.blit(backup,(0,0))
                return
    
    def process_input(self):
        """creates game events based on pygame events"""
        for event in pygame.event.get():
            if self.joystick:
                if event.type == pygame.JOYAXISMOTION:
                    self.gameevents.add("joyaxismotion", event.axis, event.value)
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == self.fire_button:
                        self.gameevents.add("press", "fire")
                    elif event.button == self.IFF_button:
                        self.gameevents.add("press", "iff")
                    elif event.button == self.shots_button:
                        self.gameevents.add("press", "shots")
                    elif event.button == self.pnts_button:
                        self.gameevents.add("press", "pnts")
                elif event.type == pygame.JOYBUTTONUP:
                    if event.button == self.fire_button:
                        self.gameevents.add("release", "fire")
                    elif event.button == self.IFF_button:
                        self.gameevents.add("release", "iff")
                    elif event.button == self.shots_button:
                        self.gameevents.add("release", "shots")
                    elif event.button == self.pnts_button:
                        self.gameevents.add("release", "pnts")
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == self.thrust_key:
                        self.gameevents.add("press", "thrust")
                    elif event.key == self.left_turn_key:
                        self.gameevents.add("press", "left")
                    elif event.key == self.right_turn_key:
                        self.gameevents.add("press", "right")
                    elif event.key == self.fire_key:
                        self.gameevents.add("press", "fire")
                    elif event.key == self.IFF_key:
                        self.gameevents.add("press", "iff")
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
                        self.gameevents.add("release", "iff")
                    elif event.key == self.shots_key:
                        self.gameevents.add("release", "shots")
                    elif event.key == self.pnts_key:
                        self.gameevents.add("release", "pnts")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.gameevents.add("press", "quit")
                elif event.key == self.pause_key and self.config.get_setting('General','allow_pause'):
                    self.gameevents.add("press", "pause")
    
    def process_game_logic(self):
        """processes game logic to produce game events"""
        self.ship.compute()
        for missile in self.missile_list:
            missile.compute()
        if self.fortress_exists == True:
            self.fortress.compute()
        for shell in self.shell_list:
            shell.compute()
        if self.config.get_setting('Hexagon','hex_shrink'):
            self.bighex.compute()
        if self.mine_exists:
            if self.mine_list.flag == False and self.mine_list.timer.elapsed() > self.mine_list.spawn_time:
                self.gameevents.add("spawn", "mine")
            elif self.mine_list.flag and self.mine_list.timer.elapsed() > self.mine_list.timeout:
                self.gameevents.add("timeout", "mine")
        self.mine_list.compute()
        self.check_bounds()
        #test collisions to generate game events
        self.test_collisions()
        if self.flighttimer.elapsed() > self.config.get_setting('Score','update_timer'):
            self.flighttimer.reset()
            distance = self.ship.get_distance_to_point(self.WORLD_WIDTH/2,self.WORLD_HEIGHT/2)
            flight_max_inc = self.config.get_setting('Score', 'flight_max_increment')
            dmod = 1 - (distance-self.smallhex.radius*1.125)/(self.WORLD_WIDTH/2)
            if dmod > 1.0: dmod = 1.0
            if dmod < 0.0: dmod = 0.0
            smod = max([abs(self.ship.velocity.x),abs(self.ship.velocity.y)]) / self.ship.max_vel
            def pointspace (a0,a1,a2,b0,b1,b2): return math.exp(a1**(a0*a2)) * math.exp(b1**(b0*b2))
            points = flight_max_inc * pointspace(dmod,2,1,smod,2,1.75) / pointspace(1,2,1,1,2,1.75)
            self.gameevents.add("score+", "flight", points)
            if (self.ship.velocity.x **2 + self.ship.velocity.y **2)**0.5 < self.config.get_setting('Score','speed_threshold'):
                self.gameevents.add("score+", "vlcty", self.config.get_setting('Score','VLCTY_increment'))
                #self.gameevents.add("score+", "flight", self.config.get_setting('Score','VLCTY_increment'))
            else:
                self.gameevents.add("score-", "vlcty", self.config.get_setting('Score','VLCTY_increment'))
                #self.gameevents.add("score-", "flight", self.config.get_setting('Score','VLCTY_increment'))
            if self.bighex.collide(self.ship):
                self.gameevents.add("score+", "cntrl", self.config.get_setting('Score','CNTRL_increment'))
                #self.gameevents.add("score+", "flight", self.config.get_setting('Score','CNTRL_increment'))
            else:
                self.gameevents.add("score+", "cntrl", self.config.get_setting('Score','CNTRL_increment')/2)
                #self.gameevents.add("score+", "flight", self.config.get_setting('Score','CNTRL_increment')/2)
        if self.bonus_exists:
            if self.config.get_setting('General','bonus_system') == "AX-CPT":
                self.bonus.axcpt_update()
            else:
                if self.bonus.visible == False and self.bonus.timer.elapsed() > self.config.get_setting('Bonus','symbol_down_time'):
                    self.gameevents.add("activate", "bonus")
                elif self.bonus.visible == True and self.bonus.timer.elapsed() >= self.config.get_setting('Bonus','symbol_up_time'):
                    self.gameevents.add("deactivate", "bonus", self.bonus.current_symbol)
        #update scores
        self.score.pnts = self.score.__getattribute__("pnts")
        self.score.vlcty = self.score.__getattribute__("vlcty")
        self.score.cntrl = self.score.__getattribute__("cntrl")
        self.score.speed = self.score.__getattribute__("speed")
        self.score.flight = self.score.__getattribute__("flight")
        self.score.fortress = self.score.__getattribute__("fortress")
        self.score.mines = self.score.__getattribute__("mines")
        self.score.bonus = self.score.__getattribute__("bonus")
    
    def process_events(self):
        """processes internal list of game events for this frame"""
        while len(self.gameevents) > 0:
            currentevent = self.gameevents.pop(0)
            time = currentevent.time
            ticks = currentevent.ticks
            eid = currentevent.eid
            game = currentevent.game
            command = currentevent.command
            obj = currentevent.obj
            target = currentevent.target
            if self.config.get_setting('Logging','logging') and currentevent.log:
                self.log.write("EVENT\t%f\t%d\t%d\t%d\t%s\t%s\t%s\n"%(time, ticks, game, eid, command, obj, target))
            if command == "press":
                if obj == "pause":
                    self.pause_game()
                elif obj == "quit":
                    self.quit(1)
                elif obj == "left":
                    self.ship.turn_left_flag = True
                elif obj == "right":
                    self.ship.turn_right_flag = True
                elif obj == "thrust":
                    self.ship.thrust_flag = True
                elif obj == "fire":
                    self.ship.fire()
                elif obj == "iff":
                    #print len(self.mine_list)
                    #don't do anything if there's no mine on the screen
                    if len(self.mine_list) == 0:
                        pass
                    elif self.mine_list[0].tagged == "fail":
                        self.gameevents.add("tag", "already_failed")
                    elif self.mine_list[0].tagged == "tagged":
                        self.gameevents.add("tag", "already_tagged")
                    #if the mine is untagged and this is the first tap
                    elif self.mine_list[0].tagged == "untagged" and self.mine_list.iff_flag == False:
                        if self.score.iff in self.mine_list.foe_letters:
                            self.gameevents.add("first_tag", "foe")
                        else:
                            self.gameevents.add("first_tag", "friend_fail")
                    #if the mine is a foe, untagged, and this is the second tap, check timer, set intrvl
                    elif self.mine_list[0].tagged == "untagged" and self.mine_list.iff_flag:
                        self.score.intrvl = self.mine_list.iff_timer.elapsed()
                        if (self.mine_list.iff_timer.elapsed() > self.config.get_setting('Mine','intrvl_min')) and (self.mine_list.iff_timer.elapsed() < self.config.get_setting('Mine','intrvl_max')):
                            self.gameevents.add("second_tag", "foe")
                        else:
                            self.gameevents.add("second_tag", "out_of_bounds")
                elif obj == "shots":
                    if self.config.get_setting('General','bonus_system') == "standard":
                        #if current symbol is bonus but previous wasn't, set flag to deny bonus if next symbol happens to be the bonus symbol
                        if (self.bonus.current_symbol == self.bonus.bonus_symbol) and (self.bonus.prior_symbol != self.bonus.bonus_symbol):
                            self.bonus.flag = True
                            self.gameevents.add("flagged_for_first_bonus")
                        if (self.bonus.current_symbol == self.bonus.bonus_symbol) and (self.bonus.prior_symbol == self.bonus.bonus_symbol):
                            #bonus available, check flag to award or deny bonus
                            if self.bonus.flag:
                                self.gameevents.add("attempt_to_capture_flagged_bonus")
                            else:
                                self.gameevents.add("shots_bonus_capture")
                                self.gameevents.add("score+", "shots", self.config.get_setting('Score','bonus_missiles'))
                                self.gameevents.add("score+", "bonus", self.config.get_setting('Score','bonus_points')/2)
                                self.bonus.flag = True
                    else: #AX-CPT
                        if self.bonus.axcpt_flag == True and (self.bonus.state == "iti" or self.bonus.state == "target") and self.bonus.current_pair == "ax":
                            self.sounds.bonus_success.play()
                            self.gameevents.add("shots_bonus_capture")
                            self.gameevents.add("score+", "shots", self.config.get_setting('Score','bonus_missiles'))
                            self.gameevents.add("score+", "bonus", self.config.get_setting('Score','bonus_points')/2)
                        elif self.bonus.axcpt_flag:
                            self.bonus.axcpt_flag = False
                            self.sounds.bonus_fail.play()
                            self.gameevents.add("shots_bonus_failure")
                            self.gameevents.add("score-", "bonus", self.config.get_setting('Score','bonus_points')/2)
                elif obj == "pnts":
                    if self.config.get_setting('General','bonus_system') == "standard":
                    #if current symbol is bonus but previous wasn't, set flag to deny bonus if next symbol happens to be the bonus symbol
                        if (self.bonus.current_symbol == self.bonus.bonus_symbol) and (self.bonus.prior_symbol != self.bonus.bonus_symbol):
                            self.bonus.flag = True
                            self.gameevents.add("flagged_for_first_bonus")
                        if (self.bonus.current_symbol == self.bonus.bonus_symbol) and (self.bonus.prior_symbol == self.bonus.bonus_symbol):
                            #bonus available, check flag to award or deny bonus
                            if self.bonus.flag:
                                self.gameevents.add("attempt_to_capture_flagged_bonus")
                            else:
                                self.gameevents.add("pnts_pnts_capture")
                                self.gameevents.add("score+", "bonus", self.config.get_setting('Score','bonus_points'))
                                self.gameevents.add("score+", "pnts", self.config.get_setting('Score','bonus_points'))
                                self.bonus.flag = True
                    else: #AX-CPT
                        if self.bonus.axcpt_flag == True and (self.bonus.state == "iti" or self.bonus.state == "target") and self.bonus.current_pair == "ax":
                            self.sounds.bonus_success.play()
                            self.gameevents.add("pnts_bonus_capture")
                            self.gameevents.add("score+", "bonus", self.config.get_setting('Score','bonus_points'))
                            self.gameevents.add("score+", "pnts", self.config.get_setting('Score','bonus_points'))
                        elif self.bonus.axcpt_flag:
                            self.bonus.axcpt_flag = False
                            self.sounds.bonus_fail.play()
                            self.gameevents.add("pnts_bonus_failure")
                            self.gameevents.add("score-", "bonus", self.config.get_setting('Score','bonus_points')/2)
            elif command == "first_tag":
                if obj == "foe":
                    self.mine_list.iff_flag = True
                    self.mine_list.iff_timer.reset()
                else:
                    self.mine_list[0].tagged = "fail"
            elif command == "second_tag":
                self.mine_list.iff_flag = False
                if obj == "foe":
                    self.mine_list[0].tagged = "tagged"                    
            elif command == "release":
                if obj == "left":
                    self.ship.turn_left_flag = False
                elif obj == "right":
                    self.ship.turn_right_flag = False
                elif obj == "thrust":
                    self.ship.thrust_flag = False
            elif command == "warp":
                self.gameevents.add("score-", "pnts", self.config.get_setting('Score','warp_penalty'))
                self.gameevents.add("score-", "flight", self.config.get_setting('Score','warp_penalty')) 
            elif command == "activate":
                if obj == "bonus":
                    self.bonus.visible = True
                    self.bonus.timer.reset()
                    self.bonus.get_new_symbol()
                    self.gameevents.add("new_bonus", self.bonus.current_symbol, self.bonus.prior_symbol)
                    if self.bonus.current_symbol == self.bonus.prior_symbol == self.bonus.bonus_symbol:
                        self.gameevents.add("bonus_available")
                    #"reset" the bonus flag (which prevents premature capture) if symbol is not bonus
                    if self.bonus.current_symbol != self.bonus.bonus_symbol:
                        self.bonus.flag = False
            elif command == "deactivate":
                if obj == "bonus":
                    self.bonus.visible = False
                    self.bonus.timer.reset()
            elif command == "spawn":
                self.mine_list.flag = True
                self.mine_list.timer.reset()
                self.mine_list.add()
                if self.mine_list[0].iff in self.mine_list.foe_letters:
                    self.gameevents.add("new_mine", "foe")
                else:
                    self.gameevents.add("new_mine", "friend")
            elif command == "timeout":
                self.mine_list.flag = False
                self.mine_list.iff_flag = False
                self.mine_list.timer.reset()
                if len(self.mine_list) > 0:
                    del self.mine_list[0]
                self.score.iff = ''
                self.score.intrvl = 0
                self.gameevents.add("score-", "mines", self.config.get_setting('Score','mine_timeout_penalty'))
            elif command == "score+":
                self.score.__setattr__(obj, self.score.__getattribute__(obj) + target)
                if self.score.shots > self.config.get_setting('Missile','missile_max'):
                    self.score.shots = self.config.get_setting('Missile','missile_max')
            elif command == "score-":
                self.score.__setattr__(obj, self.score.__getattribute__(obj) - target)
            elif command == "collide":
                self.process_collision(obj, target)
            elif command == "joyaxismotion":
                if obj == 0:
                    self.ship.joy_turn = target
                elif obj == 1:
                    self.ship.joy_thrust = target
                    
    
    def process_collision(self, obj, target):
        """process single collision event"""
        if obj == "small_hex" and not self.smallhex.small_hex_flag:
            self.ship.velocity.x = -self.ship.velocity.x
            self.ship.velocity.y = -self.ship.velocity.y
            self.gameevents.add("score-", "pnts", self.config.get_setting('Score','small_hex_penalty'))
            self.gameevents.add("score-", "flight", self.config.get_setting('Score','small_hex_penalty'))
            self.smallhex.small_hex_flag = True
        elif obj == "shell":
            #remove shell, target is index of shell in shell_list
            del self.shell_list[target]
            self.gameevents.add("score-", "pnts", self.config.get_setting('Score','shell_hit_penalty'))
            self.gameevents.add("score-", "fortress", self.config.get_setting('Score','shell_hit_penalty'))
            self.ship.take_damage()
            if not self.ship.alive:
                self.gameevents.add("destroyed", "ship", "shell")
                self.gameevents.add("score-", "pnts", self.config.get_setting('Score','ship_death_penalty'))
                self.gameevents.add("score-", "fortress", self.config.get_setting('Score','ship_death_penalty'))
                self.ship.color = (255,255,0)
            elif self.config.get_setting('Ship','colored_damage'):
                g = 255 / self.ship.start_health * (self.ship.health-1)
                self.ship.color = (255,g,0)
                
        elif obj.startswith("missile_"):
            #if missile hits fortress, need to check if it takes damage when mine is onscreen
            if target == "fortress" and (len(self.mine_list) == 0 or self.config.get_setting('Fortress','hit_fortress_while_mine')):
                if self.ship.shot_timer.elapsed() >= self.config.get_setting('Fortress','vlner_time'):
                    self.gameevents.add("score+", "vlner", 1)
                if self.ship.shot_timer.elapsed() < self.config.get_setting('Fortress','vlner_time') and self.score.vlner >= self.config.get_setting('Fortress','vlner_threshold'):
                    self.gameevents.add("destroyed", "fortress")
                    self.fortress.alive = False
                    self.fortress.reset_timer.reset()
                    self.sounds.explosion.play()
                    self.gameevents.add("score+", "pnts", self.config.get_setting('Score','destroy_fortress'))
                    self.gameevents.add("score+", "fortress", self.config.get_setting('Score','destroy_fortress'))
                    self.score.vlner = 0
                    #do we reset the mine timer?
                    if self.config.get_setting('Mine','fortress_resets_mine'):
                        self.mine_list.timer.reset()
                        self.mine_list.flag = False
                if self.ship.shot_timer.elapsed() < self.config.get_setting('Fortress','vlner_time') and self.score.vlner < self.config.get_setting('Fortress','vlner_threshold'):
                    self.gameevents.add("reset", "VLNER")
                    self.score.vlner = 0
                    self.sounds.vlner_reset.play()
                self.ship.shot_timer.reset()
            elif target.startswith("mine_"):
                #deal with missile hitting mine
                #can the mine be hit?
                if self.mine_list[0].tagged == "fail":
                    self.gameevents.add("collide", "fail_tagged_mine")
                elif self.mine_list[0].tagged == "untagged":
                    if self.score.iff in self.mine_list.foe_letters:
                        self.gameevents.add("collide", "untagged_foe_mine")
                    else:
                        self.gameevents.add("collide", "friend_mine")
                elif self.mine_list[0].tagged == "tagged" and self.score.iff in self.mine_list.foe_letters:
                    self.gameevents.add("collide", "tagged_foe_mine")
        elif obj.startswith("mine_"):
            #mine hit the ship
            index = int(obj[-1])
            del self.mine_list[index]
            self.score.iff = ''
            self.score.intrvl = 0
            self.mine_list.flag = False
            self.mine_list.iff_flag = False
            self.mine_list.timer.reset()
            self.gameevents.add("score-", "pnts", self.config.get_setting('Score','mine_hit_penalty'))
            self.gameevents.add("score-", "mines", self.config.get_setting('Score','mine_hit_penalty'))
            self.ship.take_damage()
            if not self.ship.alive:
                self.gameevents.add("destroyed", "ship", "shell")
                self.gameevents.add("score-", "pnts", self.config.get_setting('Score','ship_death_penalty'))
                self.gameevents.add("score-", "mines", self.config.get_setting('Score','ship_death_penalty'))
                self.ship.color = (255,255,0)
            elif self.config.get_setting('Ship','colored_damage'):
                g = 255 / self.ship.start_health * (self.ship.health-1)
                self.ship.color = (255,g,0)
        elif obj == "friend_mine":
            #get rid of mine
            self.mine_list.flag = False
            self.mine_list.iff_flag = False
            self.mine_list.timer.reset()
            self.gameevents.add("score+", "mines", self.config.get_setting('Score','energize_friend'))
            #amazingly, missile can hit the mine in the same frame as the mine hits the ship
            if len(self.mine_list) > 0:
                del self.mine_list[0]
            self.score.iff = ''
            self.score.intrvl = 0
        elif obj == "tagged_foe_mine":
            #get rid of mine
            self.mine_list.flag = False
            self.mine_list.iff_flag = False
            self.mine_list.timer.reset()
            self.gameevents.add("score+", "mines", self.config.get_setting('Score','destroy_foe'))
            if len(self.mine_list) > 0:
                del self.mine_list[0]
            self.score.iff = ''
            self.score.intrvl = 0
    
        
    def test_collisions(self):
        """test collisions between relevant game entities"""
        if self.smallhex.collide(self.ship):
            self.gameevents.add("collide", "small_hex", "ship")
        else:
            self.smallhex.small_hex_flag = False
        for i, shell in enumerate(self.shell_list):
            if shell.collide(self.ship):
                self.gameevents.add("collide", "shell", i)
        #need to treat this carefully - the mine can overlap the fortress, so we don't want to remove the same missile twice
        for i, missile in enumerate(self.missile_list):
            del_missile = False
            if self.fortress_exists and missile.collide(self.fortress):
                self.gameevents.add("collide", "missile_"+str(i), "fortress")
                del_missile = True
            for j, mine in enumerate(self.mine_list):
                if missile.collide(mine) and not missile.collide(self.fortress):
                    self.gameevents.add("collide", "missile_"+str(i), "mine_"+str(j))
                    del_missile = True
            if del_missile:
                del self.missile_list[i]
        for i, mine in enumerate(self.mine_list):
            if mine.collide(self.ship):
                self.gameevents.add("collide", "mine_"+str(i), "ship")
    
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
        self.ship.position.x = self.config.get_setting('Ship','ship_pos_x')*self.aspect_ratio
        self.ship.position.y = self.config.get_setting('Ship','ship_pos_y')*self.aspect_ratio
        self.ship.velocity.x = self.config.get_setting('Ship','ship_vel_x')
        self.ship.velocity.y = self.config.get_setting('Ship','ship_vel_y')
        self.ship.orientation = self.config.get_setting('Ship','ship_orientation')
    
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
        self.mine_list.draw()
        if self.bonus_exists:
            if self.bonus.visible:
                self.bonus.draw(self.worldsurf)
        self.screen.blit(self.scoresurf, self.scorerect)
        self.screen.blit(self.worldsurf, self.worldrect)
        self.gameevents.add("display", 'preflip', 'main', False)
        pygame.display.flip()
        
    def log_world(self):
        """logs current state of world to logfile"""
        #Please use tabs between columns, and wrap cells with spaces in them in quotes, like the column with the
        #list of shells
        #self.log.write("%f %d\n"%(time.time(), pygame.time.get_ticks()))
        #KEEP TRACK OF BOTH SCORES!
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
            distance = self.ship.get_distance_to_point(self.WORLD_WIDTH/2,self.WORLD_HEIGHT/2)
        else:
            ship_alive = "n"
            ship_x = ""
            ship_y = ""
            ship_vel_x = ""
            ship_vel_y = ""
            ship_orientation = ""
            distance = 0
        if len(self.mine_list) > 0:
            mine_alive = "y"
            mine_x = "%.3f"%(self.mine_list[0].position.x)
            mine_y = "%.3f"%(self.mine_list[0].position.y)
        else:
            mine_alive = "n"
            mine_x = ""
            mine_y = ""
        if self.fortress_exists and self.fortress.alive:
            fortress_alive = "y"
            fortress_orientation = str(self.fortress.orientation)
        else:
            fortress_alive = "n"
            fortress_orientation = ""
        missile = '"'
        for m in self.missile_list:
            missile += "%.3f %.3f "%(m.position.x, m.position.y)
        missile.rstrip()
        missile += '"'
        shell = '"'
        for s in self.shell_list:
            shell += "%.3f %.3f "%(s.position.x, s.position.y)
        shell.rstrip()
        shell += '"'
        if self.config.get_setting('General','bonus_system') == "AX-CPT":
            bonus_isi = str(self.bonus.isi_time)
        else:
            bonus_isi = ''
        if self.bonus.visible:
            bonus_cur_x = self.bonus.x
            bonus_cur_y = self.bonus.y
        else:
            bonus_cur_x = ""
            bonus_cur_y =  ""
        if self.bonus.current_symbol == '':
            bonus_cur = ""
        else:
            bonus_cur = self.bonus.current_symbol
        if self.bonus.prior_symbol == '':
            bonus_prev = ""
        else:
            bonus_prev = self.bonus.prior_symbol
        if self.score.iff == '':
            iff_score = ''
        else:
            iff_score = self.score.iff
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
        
        self.log.write("STATE\t%f\t%d\t%d\t\t\t\t\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t" %
                       (system_clock, game_time, self.current_game, " ".join(self.mine_list.foe_letters), ship_alive, ship_x, ship_y, ship_vel_x, ship_vel_y, ship_orientation,
                        distance, mine_alive, mine_x, mine_y, fortress_alive, fortress_orientation, missile, shell))
        if self.config.get_setting('General','bonus_system') == "AX-CPT":
            self.log.write("%s\t%s\t%s\t%s\t%s\t" %
                           (bonus_prev, bonus_cur, bonus_cur_x, bonus_cur_y, bonus_isi))
        else:
            self.log.write("%s\t%s\t%s\t%s\t" %
                           (bonus_prev, bonus_cur, bonus_cur_x, bonus_cur_y))
        self.log.write("%d\t%d\t%d\t%d\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s" %
                       (self.score.pnts, self.score.cntrl, self.score.vlcty, self.score.vlner, iff_score, self.score.intrvl, self.score.speed, self.score.shots, self.score.flight, self.score.fortress, 
                        self.score.mines, self.score.bonus, thrust_key, left_key, right_key, fire_key, iff_key, shots_key, pnts_key))
        for name in self.plugins:
            try:
                data = self.plugins[name].logCallback()
                if data:
                    self.log.write(data)
            except AttributeError:
                pass
        self.log.write("\n")

    def display_intro(self):
        """display intro scene"""
        font1 = pygame.font.Font(self.fp, int(self.SCREEN_HEIGHT/10))
        title = font1.render(get_psf_version_string(), True, (255,200,100))
        title_rect = title.get_rect()
        title_rect.center = (self.SCREEN_WIDTH/2,self.SCREEN_HEIGHT/5)
        fh = int(self.SCREEN_HEIGHT/72)
        font2 = pygame.font.Font(self.fp, fh)
        vers = font2.render('Version: %s' % (githash), True, (255,200,100))
        vers_rect = vers.get_rect()
        vers_rect.center = (self.SCREEN_WIDTH/2,4*self.SCREEN_HEIGHT/5 - fh/2 - 2)
        copy = font2.render('Copyright \xa92011 CogWorks Laboratory, Rensselaer Polytechnic Institute', True, (255,200,100))
        copy_rect = copy.get_rect()
        copy_rect.center = (self.SCREEN_WIDTH/2,4*self.SCREEN_HEIGHT/5 + fh/2 + 2)
        scale = .4 * self.SCREEN_HEIGHT / 128
        logo = picture.Picture(os.path.join(self.approot, 'psf5.png'), scale)
        logo.rect.center = (self.SCREEN_WIDTH/2,self.SCREEN_HEIGHT/2)
        self.screen.fill((0,0,0))
        self.screen.blit(title, title_rect)
        self.screen.blit(vers, vers_rect)
        self.screen.blit(copy, copy_rect)
        self.screen.blit(logo.image, logo.rect)
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    return
        
    def display_foe_mines(self):
        """before game begins, present the list of IFF letters to target"""
        self.screen.fill((0,0,0))
        top = self.f24.render("The Type-2 mines for this session are:", True, (255,255,0))
        top_rect = top.get_rect()
        top_rect.centerx = self.SCREEN_WIDTH/2
        top_rect.centery = 270*self.aspect_ratio
        middle = self.f96.render(", ".join(self.mine_list.foe_letters), True, (255,255,255))
        middle_rect = middle.get_rect()
        middle_rect.centerx = self.SCREEN_WIDTH/2
        middle_rect.centery =self.SCREEN_HEIGHT/2
        midbot = self.f24.render("Try to memorize them before proceeding", True, (255,255,0))
        midbot_rect = midbot.get_rect()
        midbot_rect.centerx = self.SCREEN_WIDTH/2
        midbot_rect.centery = 500*self.aspect_ratio
        bottom = self.f24.render("Press any key to begin", True, (255,255,0))
        bottom_rect = bottom.get_rect()
        bottom_rect.centerx = self.SCREEN_WIDTH/2
        bottom_rect.centery = 600*self.aspect_ratio
        self.screen.blit(top, top_rect)
        self.screen.blit(middle, middle_rect)
        self.screen.blit(midbot, midbot_rect)
        self.screen.blit(bottom, bottom_rect)
        pygame.display.flip()
        self.gameevents.add("display_foes", " ".join(self.mine_list.foe_letters), "player")
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    return
                    
    def fade(self):
        """fade screen to show score"""
        fadesurf = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT)).convert_alpha()
        fadesurf.fill((0,0,0,12))
        for i in range(50):
            self.screen.blit(fadesurf, pygame.Rect(0,0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            pygame.display.flip()

    def show_old_score(self):
        """shows score for last game and waits to continue"""
        pygame.event.get() #clear event list? Otherwise it skips
        self.screen.fill((0, 0, 0))
        #sessionsurf = self.f24.render("Session %d, Game %d/%s"%(self.session_number, self.game_number, self.config["games_per_session"]), True, (255,255,255))
        # sessionrect = sessionsurf.get_rect()
        # sessionrect.centerx = self.SCREEN_WIDTH / 2
        # sessionrect.y = 100
        # self.screen.blit(sessionsurf, sessionrect)
        gamesurf = self.f36.render("Game %d" % (self.current_game), True, (255,255,0))
        gamerect = gamesurf.get_rect()
        gamerect.centery = self.SCREEN_HEIGHT / 16 * 2
        gamerect.centerx = self.SCREEN_WIDTH / 2
        self.screen.blit(gamesurf, gamerect)
        pygame.draw.line(self.screen, (255, 255, 255), (self.SCREEN_WIDTH / 4 , self.SCREEN_HEIGHT / 16 * 3), (self.SCREEN_WIDTH / 4 * 3, self.SCREEN_HEIGHT / 16 * 3))
        pntssurf = self.f24.render("PNTS score:", True, (255, 255,0))
        pntsrect = pntssurf.get_rect()
        pntsrect.left = self.SCREEN_WIDTH / 3
        pntsrect.centery = self.SCREEN_HEIGHT / 16 * 4
        self.screen.blit(pntssurf, pntsrect)
        cntrlsurf = self.f24.render("CNTRL score:", True, (255, 255,0))
        cntrlrect = cntrlsurf.get_rect()
        cntrlrect.left = self.SCREEN_WIDTH / 3 
        cntrlrect.centery = self.SCREEN_HEIGHT / 16 * 6
        self.screen.blit(cntrlsurf, cntrlrect)
        vlctysurf = self.f24.render("VLCTY score:", True, (255, 255,0))
        vlctyrect = vlctysurf.get_rect()
        vlctyrect.left = self.SCREEN_WIDTH / 3
        vlctyrect.centery = self.SCREEN_HEIGHT / 16 * 8
        self.screen.blit(vlctysurf, vlctyrect)
        speedsurf = self.f24.render("SPEED score:", True, (255, 255,0))
        speedrect = speedsurf.get_rect()
        speedrect.left = self.SCREEN_WIDTH / 3
        speedrect.centery = self.SCREEN_HEIGHT / 16 * 10 
        self.screen.blit(speedsurf, speedrect)
        pntsnsurf = self.f24.render("%d"%self.score.pnts, True, (255, 255,255))
        pntsnrect = pntsnsurf.get_rect()
        pntsnrect.right = self.SCREEN_WIDTH / 3 * 2
        pntsnrect.centery = self.SCREEN_HEIGHT / 16 * 4
        self.screen.blit(pntsnsurf, pntsnrect)
        cntrlnsurf = self.f24.render("%d"%self.score.cntrl, True, (255, 255,255))
        cntrlnrect = cntrlnsurf.get_rect()
        cntrlnrect.right = self.SCREEN_WIDTH / 3 * 2
        cntrlnrect.centery = self.SCREEN_HEIGHT / 16 * 6
        self.screen.blit(cntrlnsurf, cntrlnrect)
        vlctynsurf = self.f24.render("%d"%self.score.vlcty, True, (255, 255,255))
        vlctynrect = vlctynsurf.get_rect()
        vlctynrect.right = self.SCREEN_WIDTH / 3 * 2
        vlctynrect.centery = self.SCREEN_HEIGHT / 16 * 8
        self.screen.blit(vlctynsurf, vlctynrect)
        speednsurf = self.f24.render("%d"%self.score.speed, True, (255, 255,255))
        speednrect = speednsurf.get_rect()
        speednrect.right = self.SCREEN_WIDTH / 3 * 2
        speednrect.centery = self.SCREEN_HEIGHT / 16 * 10
        self.screen.blit(speednsurf, speednrect)
        #draw line
        pygame.draw.line(self.screen, (255, 255, 255), (self.SCREEN_WIDTH / 4 , self.SCREEN_HEIGHT / 16 * 11), (self.SCREEN_WIDTH / 4 * 3, self.SCREEN_HEIGHT / 16 * 11))
        totalsurf = self.f24.render("Total game score:", True, (255, 255,0))
        totalrect = totalsurf.get_rect()
        totalrect.left = self.SCREEN_WIDTH / 3
        totalrect.centery = self.SCREEN_HEIGHT / 16 * 12
        self.screen.blit(totalsurf, totalrect)
        totalnsurf = self.f24.render("%d"%(self.score.pnts + self.score.cntrl + self.score.vlcty + self.score.speed), True, (255, 255,255))
        totalnrect = totalnsurf.get_rect()
        totalnrect.right = self.SCREEN_WIDTH / 3 * 2
        totalnrect.centery = self.SCREEN_HEIGHT / 16 * 12
        self.screen.blit(totalnsurf, totalnrect)
        # if self.game_number == int(self.config["games_per_session"]):
        if self.current_game == self.config.get_setting('General','games_per_session'):
            finalsurf = self.f24.render("You're done! Press any key to exit", True, (0,255,0))
        else:
            finalsurf = self.f24.render("Press any key for next game", True, (0,255,0))
        # else:
        #            finalsurf = self.f24.render("Press any key to continue to next game or ESC to exit", True, (255,255,255))
        finalrect = finalsurf.get_rect()
        finalrect.centerx = self.SCREEN_WIDTH /2
        finalrect.centery = self.SCREEN_HEIGHT / 16 * 14
        self.screen.blit(finalsurf, finalrect)
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.quit(1)
                    else:
                        return
                        
    def show_new_score(self):
        """shows score for last game and waits to continue"""
        pygame.event.get() #clear event list? Otherwise it skips
        self.screen.fill((0, 0, 0))
        #sessionsurf = self.f24.render("Session %d, Game %d/%s"%(self.session_number, self.game_number, self.config["games_per_session"]), True, (255,255,255))
        # sessionrect = sessionsurf.get_rect()
        # sessionrect.centerx = self.SCREEN_WIDTH / 2
        # sessionrect.y = 100
        # self.screen.blit(sessionsurf, sessionrect)
        gamesurf = self.f36.render("Game %d" % (self.current_game), True, (255,255,0))
        gamerect = gamesurf.get_rect()
        gamerect.centery = self.SCREEN_HEIGHT / 16 * 2
        gamerect.centerx = self.SCREEN_WIDTH / 2
        self.screen.blit(gamesurf, gamerect)
        pygame.draw.line(self.screen, (255, 255, 255), (self.SCREEN_WIDTH / 4 , self.SCREEN_HEIGHT / 16 * 3), (self.SCREEN_WIDTH / 4 * 3, self.SCREEN_HEIGHT / 16 * 3))
        pntssurf = self.f24.render("Flight score:", True, (255, 255,0))
        pntsrect = pntssurf.get_rect()
        pntsrect.left = self.SCREEN_WIDTH / 3
        pntsrect.centery = self.SCREEN_HEIGHT / 16 * 4
        self.screen.blit(pntssurf, pntsrect)
        cntrlsurf = self.f24.render("Fortress score:", True, (255, 255,0))
        cntrlrect = cntrlsurf.get_rect()
        cntrlrect.left = self.SCREEN_WIDTH / 3 
        cntrlrect.centery = self.SCREEN_HEIGHT / 16 * 6
        self.screen.blit(cntrlsurf, cntrlrect)
        vlctysurf = self.f24.render("Mine score:", True, (255, 255,0))
        vlctyrect = vlctysurf.get_rect()
        vlctyrect.left = self.SCREEN_WIDTH / 3
        vlctyrect.centery = self.SCREEN_HEIGHT / 16 * 8
        self.screen.blit(vlctysurf, vlctyrect)
        speedsurf = self.f24.render("Bonus score:", True, (255, 255,0))
        speedrect = speedsurf.get_rect()
        speedrect.left = self.SCREEN_WIDTH / 3
        speedrect.centery = self.SCREEN_HEIGHT / 16 * 10
        self.screen.blit(speedsurf, speedrect)
        pntsnsurf = self.f24.render("%d"%self.score.flight, True, (255, 255,255))
        pntsnrect = pntsnsurf.get_rect()
        pntsnrect.right = self.SCREEN_WIDTH / 3 * 2
        pntsnrect.centery = self.SCREEN_HEIGHT / 16 * 4
        self.screen.blit(pntsnsurf, pntsnrect)
        cntrlnsurf = self.f24.render("%d"%self.score.fortress, True, (255, 255,255))
        cntrlnrect = cntrlnsurf.get_rect()
        cntrlnrect.right = self.SCREEN_WIDTH / 3 * 2
        cntrlnrect.centery = self.SCREEN_HEIGHT / 16 * 6
        self.screen.blit(cntrlnsurf, cntrlnrect)
        vlctynsurf = self.f24.render("%d"%self.score.mines, True, (255, 255,255))
        vlctynrect = vlctynsurf.get_rect()
        vlctynrect.right = self.SCREEN_WIDTH / 3 * 2
        vlctynrect.centery = self.SCREEN_HEIGHT / 16 * 8
        self.screen.blit(vlctynsurf, vlctynrect)
        speednsurf = self.f24.render("%d"%self.score.bonus, True, (255, 255,255))
        speednrect = speednsurf.get_rect()
        speednrect.right = self.SCREEN_WIDTH / 3 * 2
        speednrect.centery = self.SCREEN_HEIGHT / 16 * 10
        self.screen.blit(speednsurf, speednrect)
        #draw line
        pygame.draw.line(self.screen, (255, 255, 255), (self.SCREEN_WIDTH / 4 , self.SCREEN_HEIGHT / 16 * 11), (self.SCREEN_WIDTH / 4 * 3, self.SCREEN_HEIGHT / 16 * 11))
        totalsurf = self.f24.render("Total game score:", True, (255, 255,0))
        totalrect = totalsurf.get_rect()
        totalrect.left = self.SCREEN_WIDTH / 3
        totalrect.centery = self.SCREEN_HEIGHT / 16 * 12
        self.screen.blit(totalsurf, totalrect)
        totalnsurf = self.f24.render("%d"%(self.score.flight + self.score.fortress + self.score.mines + self.score.bonus), True, (255, 255,255))
        totalnrect = totalnsurf.get_rect()
        totalnrect.right = self.SCREEN_WIDTH / 3 * 2
        totalnrect.centery = self.SCREEN_HEIGHT / 16 * 12
        self.screen.blit(totalnsurf, totalnrect)
        # if self.game_number == int(self.config["games_per_session"]):
        if self.current_game == self.config.get_setting('General','games_per_session'):
            finalsurf = self.f24.render("You're done! Press any key to exit", True, (0,255,0))
        else:
            finalsurf = self.f24.render("Press any key for next game", True, (0,255,0))
        # else:
        #            finalsurf = self.f24.render("Press any key to continue to next game or ESC to exit", True, (255,255,255))
        finalrect = finalsurf.get_rect()
        finalrect.centerx = self.SCREEN_WIDTH /2
        finalrect.centery = self.SCREEN_HEIGHT / 16 * 14
        self.screen.blit(finalsurf, finalrect)
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.quit(1)
                    else:
                        return
    
    def quit(self, ret=0):
        self.gameevents.add("game", "quit", ret)
        self.process_events()
        if self.config.get_setting('Logging','logging'):
            self.log.close()
        pygame.quit()
        sys.exit(ret)

def main():
    
    g = Game()
    g.display_intro()
    while g.current_game < g.config.get_setting('General','games_per_session'):
        g.current_game += 1
        g.gameevents.add("game", "ready")
        if g.mine_exists:
            g.display_foe_mines()
        g.setup_world()
        gameTimer = tokens.timer.Timer()
        g.gameevents.add("game","start")
        while True:
            g.clock.tick(30)
            g.process_input()
            g.process_game_logic()
            g.process_events()              
            g.draw()
            if g.config.get_setting('Logging','logging'):
                g.log_world()
            if g.ship.alive == False:
                g.reset_position()
            if gameTimer.elapsed() > g.config.get_setting('General','game_time'):
                g.gameevents.add("game","end")
                g.fade()
                g.gameevents.add("scores","show")
                if g.config.get_setting('Score','new_scoring'):
                    g.show_new_score()
                else:
                    g.show_old_score()
                g.gameevents.add("scores","hide")
                break
        g.gameevents.add("game", "over")
    g.quit()

if __name__ == '__main__':
    main()
        

