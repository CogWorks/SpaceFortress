from __future__ import division

import numpy as np

from twisted.internet import reactor
from twisted.internet.task import LoopingCall

import os, sys, math, copy, time, datetime, pkg_resources
from random import randrange, choice

import platform as plat

os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'

from OpenGL.GL import *
from OpenGL.GLU import *

import pygame
from pygame.locals import *
import pygl2d
from pygl2d.display import scissor_box, subspace

from gameevent import GameEvent, GameEventList
from frame import Frame
from score import Score
from sound import Sound
from timer import Timer
from hexagon import Hex
from mine import Mine, MineList
from missile import MissileList
from shell import ShellList
from ship import Ship
from bonus import Bonus
from fortress import Fortress

import defaults

get_time = time.time
if plat.system() == 'Windows':
    get_time = time.clock
def get_time_ms(): return get_time() * 1000

from version import __version__
def get_psf_version_string():
    return "Space Fortress 5"

def get_default_logdir():
    _home = os.environ.get('HOME', '/')
    if plat.system() == 'Windows':
        logdir = os.path.join(os.environ['USERPROFILE'], 'My Documents', 'Spacefortress')
    elif plat.system() == 'Linux' or plat.system() == 'Darwin':
        logdir = os.path.join(_home, 'Documents', 'Spacefortress')
    else:
        logdir = os.path.join(_home, 'Spacefortress')
    return logdir

release_build = False

class Game(object):
    """Main game application"""
    def __init__(self):
        super(Game, self).__init__()

        self.ret = 1

        self.reactor = reactor

        self.STATE_UNKNOWN = -1
        self.STATE_CALIBRATE = 0
        self.STATE_INTRO = 1
        self.STATE_SETUP = 2
        self.STATE_GAMENO = 3
        self.STATE_SETUP_IFF = 4
        self.STATE_IFF = 5
        self.STATE_PREPARE = 6
        self.STATE_PLAY = 7
        self.STATE_PAUSED = 8
        self.STATE_SCORES = 9
        self.STATE_DONE = 10

        self.state = self.STATE_INTRO

        self.ship = None
        self.bonus = None
        self.score = None
        self.fortress = None
        self.missile_list = None
        self.shell_list = None

        self.current_game = 0
        self.flight2 = 0
        self.mine2 = 0
        self.fps = 30
        self.header = {}
        self.bonus_captured = False

        self.modifier = pygame.KMOD_CTRL
        if plat.system() == 'Darwin':
            self.modifier = pygame.KMOD_META

        self.gameevents = GameEventList(self)
        self.plugins = {}
        #self.plugins = defaults.load_plugins(self, pkg_resources.resource_stream(__name__,  'plugins'), self.plugins)
        self.plugins = defaults.load_plugins(self, defaults.get_plugin_home(), self.plugins)
        for name in self.plugins:
            if hasattr(self.plugins[name], 'eventCallback'):
                self.gameevents.addCallback(self.plugins[name].eventCallback)

        self.gameevents.add("game", "version", __version__, type='EVENT_SYSTEM')

        self.config = defaults.get_config()
        if os.path.isfile('config.json'):
            self.config.set_user_file('config.json')
        else:
            self.config.set_user_file(defaults.get_user_file())
        self.gameevents.add("config", "load", "defaults", type='EVENT_SYSTEM')
        self.config.update_from_user_file()
        self.gameevents.add("config", "load", "user", type='EVENT_SYSTEM')

        for name in self.plugins:
            if hasattr(self.plugins[name], "ready"):
                self.plugins[name].ready()

        pygame.display.init()
        pygame.font.init()
        
        pygame.event.set_blocked((pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN))
        
        mode_list = pygame.display.list_modes()
        if self.config['Display']['display_mode'] == 'Windowed':
            if self.config['Display']['screen_width'] > 0 and self.config['Display']['screen_height'] > 0:
                best_mode = (self.config['Display']['screen_width'], self.config['Display']['screen_height'])
            else:
    			for mode in mode_list:
    				tmp = mode[0] / 2
    				for m in mode_list:
    					if tmp == m[0]:
    						mode_list.remove(mode)
    						break
    			best_mode = mode_list[1]
        else:
            if self.config['Display']['display_mode'] == 'Current':
                info = pygame.display.Info()
                best_mode = (info.current_w, info.current_h)
            else:
                best_mode = mode_list[0]
        self.SCREEN_WIDTH = best_mode[0]
        self.SCREEN_HEIGHT = best_mode[1]
        self.screen_size = (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        if self.config['Logging']['logging']:
            d = datetime.datetime.now().timetuple()
            base = "SpaceFortress-%s_%s_%d-%d-%d_%d-%d-%d" % (__version__, self.config['General']['id'], d[0], d[1], d[2], d[3], d[4], d[5])
            logdir = self.config['Logging']['logdir']
            if len(logdir.strip()) == 0:
                logdir = get_default_logdir()
            if not os.path.exists(logdir):
                os.makedirs(logdir)
            self.log_basename = os.path.join(logdir, base)
            self.gameevents.add("log", "basename", "ready", type='EVENT_SYSTEM')
            self.log_filename = "%s.txt.incomplete" % (self.log_basename)
            self.log = open(self.log_filename, "w")
            self.log_header = ["event_type", "system_time", "game_time",
                               "current_game", "eid", "e1", "e2", "e3", "foes", "ship_alive",
                               "ship_health", "ship_x", "ship_y", "smod", "dmod", "ship_vel_x",
                               "ship_vel_y", "ship_orientation", "distance", "mine_no", "mine_id",
                               "mine", "fortress_alive", "fortress_x", "fortress_y",
                               "fortress_orientation", "missile", "shell", "bonus_no",
                               "bonus_prev", "bonus_cur", "bonus_cur_x", "bonus_cur_y"]
            if self.config['General']['bonus_system'] == "AX-CPT":
                self.log_header.append('bonus_isi')
            self.log_header = self.log_header + ["score_pnts", "score_cntrl", "score_vlcty", "score_vlner", "score_iff",
                                                 "score_intrvl", "score_speed", "score_shots", "score_flight", "score_flight2",
                                                 "score_fortress", "score_mine", "score_mine2", "score_bonus", "thrust_key",
                                                 "left_key", "right_key", "fire_key", "iff_key", "shots_key", "pnts_key"]
            for name in self.plugins:
                if hasattr(self.plugins[name], "logHeader"):
                    self.log_header = self.log_header + self.plugins[name].logHeader()

            self.log.write("\t".join(self.log_header) + "\n")

            self.gameevents.add("log", "header", "ready", log=False, type='EVENT_SYSTEM')
            self.gameevents.add("log", "version", "8", type='EVENT_SYSTEM')

        self.gameevents.add("config", "running", str(self.config), type='EVENT_SYSTEM')

        pygame.mouse.set_visible(False)

        self.set_aspect_ratio()
        os.environ['SDL_VIDEO_WINDOW_POS'] = str(int(mode_list[0][0] / 2 - self.SCREEN_WIDTH / 2)) + "," + str(int(mode_list[0][1] / 2 - self.SCREEN_HEIGHT / 2))
        if self.config['General']['next_gen']:
            self.WORLD_WIDTH = int((710 + 57) * self.aspect_ratio)
            self.WORLD_HEIGHT = int((626 + 57) * self.aspect_ratio)
        else:
            self.WORLD_WIDTH = int(710 * self.aspect_ratio)
            self.WORLD_HEIGHT = int(626 * self.aspect_ratio)
        self.linewidth = self.config['Display']['linewidth']
        
        self.stars = []

        self.kp_space = self.linewidth
        self.kp_right = self.linewidth
        self.kp_left = self.linewidth
        self.kp_thrust = self.linewidth
        self.kp_iff = self.linewidth
        self.kp_shots = self.linewidth
        self.kp_points = self.linewidth

        self.fh = int(self.SCREEN_HEIGHT / 72)
        
        self.fp = pkg_resources.resource_stream('resources', 'fonts/freesansbold.ttf')
        self.font1 = pygame.font.Font(self.fp, int(self.SCREEN_HEIGHT / 10))
        self.fp.seek(0)
        self.font2 = pygame.font.Font(self.fp, self.fh)
        self.fp.seek(0)
        self.f = pygame.font.Font(self.fp, int(14 * self.aspect_ratio))
        self.fp.seek(0)
        self.f6 = pygame.font.Font(self.fp, int(12 * self.aspect_ratio))
        self.fp.seek(0)
        self.f24 = pygame.font.Font(self.fp, int(20 * self.aspect_ratio))
        self.fp.seek(0)
        self.f28 = pygame.font.Font(self.fp, int(28 * self.aspect_ratio))
        self.fp.seek(0)
        self.f96 = pygame.font.Font(self.fp, int(72 * self.aspect_ratio))
        self.fp.seek(0)
        self.f36 = pygame.font.Font(self.fp, int(36 * self.aspect_ratio))

        self.joystick = None
        if self.config['Joystick']['use_joystick']:
            pygame.joystick.init()
            self.joystick = pygame.joystick.Joystick(self.config['Joystick']['joystick_id'])
            self.joystick.init()
            self.fire_button = self.config['Joystick']['fire_button']
            self.IFF_button = self.config['Joystick']['iff_button']
            self.shots_button = self.config['Joystick']['shots_button']
            self.pnts_button = self.config['Joystick']['pnts_button']

        self.thrust_key = eval("pygame.K_%s" % self.config['Keybindings']['thrust_key'])
        self.left_turn_key = eval("pygame.K_%s" % self.config['Keybindings']['left_turn_key'])
        self.right_turn_key = eval("pygame.K_%s" % self.config['Keybindings']['right_turn_key'])
        self.fire_key = eval("pygame.K_%s" % self.config['Keybindings']['fire_key'])
        self.IFF_key = eval("pygame.K_%s" % self.config['Keybindings']['IFF_key'])
        self.shots_key = eval("pygame.K_%s" % self.config['Keybindings']['shots_key'])
        self.pnts_key = eval("pygame.K_%s" % self.config['Keybindings']['pnts_key'])

        self.pause_key = eval("pygame.K_%s" % self.config['Keybindings']['pause_key'])

        if self.config['General']['sound']:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(32)
        
        self.snd_shell_fired = Sound(self, pkg_resources.resource_stream("resources", "sounds/shellfired.wav"))
        self.snd_missile_fired = Sound(self, pkg_resources.resource_stream("resources", "sounds/missilefired.wav"))
        self.snd_explosion = Sound(self, pkg_resources.resource_stream("resources", "sounds/expfort.wav"))
        self.snd_collision = Sound(self, pkg_resources.resource_stream("resources", "sounds/collision.wav"))
        self.snd_vlner_reset = Sound(self, pkg_resources.resource_stream("resources", "sounds/vulnerzeroed.wav"))
        self.snd_bonus_success = Sound(self, pkg_resources.resource_stream("resources", "sounds/bonus_success.wav"))
        self.snd_bonus_fail = Sound(self, pkg_resources.resource_stream("resources", "sounds/bonus_fail.wav"))
        self.snd_empty = Sound(self, pkg_resources.resource_stream("resources", "sounds/emptychamber.wav"))
        
        if self.config['Display']['display_mode'] == 'Fullscreen' or self.config['Display']['display_mode'] == 'Current':
            self.screen = pygl2d.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.DOUBLEBUF)
        elif self.config['Display']['display_mode'] == 'Fake Fullscreen':
            self.screen = pygl2d.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.NOFRAME | pygame.DOUBLEBUF)
        else:
            self.screen = pygl2d.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.DOUBLEBUF)
        self.screen_rect = self.screen.get_rect()
        self.gameevents.add("display", 'setmode', (self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.aspect_ratio), type='EVENT_SYSTEM')

        self.gametimer = Timer(get_time_ms)
        self.flighttimer = Timer(self.gametimer.elapsed)

        self.frame = Frame(self)
        self.score = Score(self)

        self.gameevents.add("score1", self.score.scores_locations[0][0], self.score.scores_locations[0][1], type='EVENT_SYSTEM')
        self.gameevents.add("score2", self.score.scores_locations[1][0], self.score.scores_locations[1][1], type='EVENT_SYSTEM')
        self.gameevents.add("score3", self.score.scores_locations[2][0], self.score.scores_locations[2][1], type='EVENT_SYSTEM')
        self.gameevents.add("score4", self.score.scores_locations[3][0], self.score.scores_locations[3][1], type='EVENT_SYSTEM')
        self.gameevents.add("score5", self.score.scores_locations[4][0], self.score.scores_locations[4][1], type='EVENT_SYSTEM')
        self.gameevents.add("score6", self.score.scores_locations[5][0], self.score.scores_locations[5][1], type='EVENT_SYSTEM')
        self.gameevents.add("score7", self.score.scores_locations[6][0], self.score.scores_locations[6][1], type='EVENT_SYSTEM')
        self.gameevents.add("score8", self.score.scores_locations[7][0], self.score.scores_locations[7][1], type='EVENT_SYSTEM')

        if self.config['Graphics']['fancy']:
            self.explosion = pygl2d.image.Image(pkg_resources.resource_stream("resources", 'gfx/exp2.png'))
            self.explosion_rect = self.explosion.get_rect()
            self.explosion.scale(182 * self.aspect_ratio / 344)
            self.explosion.colorize(255.0, 255.0, 255.0, 204)
            self.explosion_small = pygl2d.image.Image(pkg_resources.resource_stream("resources", 'gfx/exp3.png'))
            self.explosion_small_rect = self.explosion_small.get_rect()
            self.explosion_small.scale(70 * self.aspect_ratio / 85)
            self.explosion_small.colorize(255.0, 255.0, 255.0, 204)
        else:
            self.explosion = pygl2d.image.Image(pkg_resources.resource_stream("resources", 'gfx/exp.png'))
            self.explosion_rect = self.explosion.get_rect()
            self.explosion_small = pygl2d.image.Image(pkg_resources.resource_stream("resources", 'gfx/exp.png'))
            self.explosion_small_rect = self.explosion_small.get_rect()
        
        self.world = pygame.rect.Rect(0, 0, self.WORLD_WIDTH, self.WORLD_HEIGHT)
        self.world.center = (self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2)
        if not self.config['Score']['new_scoring_pos']:
            self.world.top = 5 * self.aspect_ratio
        else:
            self.world.top = 70 * self.aspect_ratio

        self.bighex = Hex(self, self.config['Hexagon']['big_hex'])
        self.smallhex = Hex(self, self.config['Hexagon']['small_hex'])
        if self.config['Mine']['mine_exists']:
            self.mine_exists = True
        else:
            self.mine_exists = False
        self.mine_list = MineList(self)

        self.dmod = -1
        self.smod = -1
        
        self.intro_title = pygl2d.font.RenderText(get_psf_version_string(), (255, 200, 100), self.font1)
        self.intro_title_rect = self.intro_title.get_rect()
        self.intro_title_rect.center = (self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 5)
        
        self.intro_vers = pygl2d.font.RenderText('Version: %s' % (__version__), (255, 200, 100), self.font2)
        self.intro_vers_rect = self.intro_vers.get_rect()
        self.intro_vers_rect.center = (self.SCREEN_WIDTH / 2, 4 * self.SCREEN_HEIGHT / 5 - self.fh / 2 - 2)
        
        self.intro_copy = pygl2d.font.RenderText('Copyright \xa92011 CogWorks Laboratory, Rensselaer Polytechnic Institute', (255, 200, 100), self.font2)
        self.intro_copy_rect = self.intro_copy.get_rect()
        self.intro_copy_rect.center = (self.SCREEN_WIDTH / 2, 4 * self.SCREEN_HEIGHT / 5 + self.fh / 2 + 2)
        
        self.intro_logo = pygl2d.image.Image(pkg_resources.resource_stream("resources", 'gfx/psf5.png'))
        self.intro_logo_rect = self.intro_logo.get_rect()
        self.intro_logo_rect.center = (self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2)
        self.intro_logo.scale(.4 * self.SCREEN_HEIGHT / 128)

        self.pause = pygl2d.font.RenderText("Paused!", (255, 255, 255), self.f96)
        self.pause_rect = self.pause.get_rect()
        self.pause_rect.center = (self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2)
        
        self.happy = pygl2d.image.load_xbm(pkg_resources.resource_stream("resources", "gfx/fill1.xbm"))
        self.gameevents.add("session", "ready", type='EVENT_SYSTEM')

    def set_aspect_ratio(self):
        self.aspect_ratio = self.SCREEN_HEIGHT / 768
        xover = self.SCREEN_WIDTH + 2 * (495 * self.aspect_ratio - self.SCREEN_WIDTH / 2)
        if xover > self.SCREEN_WIDTH:
            self.aspect_ratio = self.SCREEN_WIDTH / 1024

    def setup_world(self):
        """initializes gameplay"""
        self.gameevents.add("game", "setup", type='EVENT_SYSTEM')
        self.missile_list = MissileList(self)
        self.shell_list = ShellList(self)
        self.ship = Ship(self)
        
        self.gametimer.reset()
        
        if self.config['Fortress']['fortress_exists']:
            self.fortress = Fortress(self)
            self.fortress_exists = True
        else:
            self.fortress_exists = False
        if self.config['Bonus']['bonus_exists']:
            self.bonus = Bonus(self)
            self.bonus_exists = True
        else:
            self.bonus_exists = False       

        self.destroyedFortresses = 0
        self.totalMines = 0
        self.destroyedMines = 0
        self.totalBonuses = 0
        self.capturedBonuses = 0
        self.deaths = 0

        self.score.pnts = 0
        self.score.cntrl = 0
        self.score.vlcty = 0
        self.score.speed = 0
        self.score.flight = 0
        self.flight2 = 0
        self.mine2 = 0
        self.score.fortress = 0
        self.score.mines = 0
        self.score.bonus = 0
        self.score.vlner = 0
        self.score.shots = self.config['Missile']['missile_num']
        
        self.flighttimer.reset()
        self.mine_list.timer.reset()
        if self.config['Graphics']['parallax_mode'] == 'Fortress':
            self.starfield_orientation = self.fortress.orientation
        else:
            self.starfield_orientation = randrange(0, 359)
        self.star_velocty_x = math.cos(math.radians(self.starfield_orientation - 180)) * self.config['Graphics']['star_speed']
        self.star_velocty_y = math.sin(math.radians(self.starfield_orientation)) * self.config['Graphics']['star_speed']
        if self.config['Graphics']['show_starfield']:
            self.init_stars()

    def draw_pause_overlay(self):
        self.pause.draw(self.pause_rect.topleft)

    def process_input(self):
        """creates game events based on pygame events"""
        for event in pygame.event.get():

            if self.joystick and self.state == self.STATE_PLAY:

                if event.type == pygame.JOYAXISMOTION:
                    self.gameevents.add("joyaxismotion", event.axis, event.value, type='EVENT_USER')
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == self.fire_button:
                        self.gameevents.add("press", "fire", type='EVENT_USER')
                    elif event.button == self.IFF_button:
                        self.gameevents.add("press", "iff", type='EVENT_USER')
                    elif event.button == self.shots_button:
                        self.gameevents.add("press", "shots", type='EVENT_USER')
                    elif event.button == self.pnts_button:
                        self.gameevents.add("press", "pnts", type='EVENT_USER')
                elif event.type == pygame.JOYBUTTONUP:
                    if event.button == self.fire_button:
                        self.gameevents.add("release", "fire", type='EVENT_USER')
                    elif event.button == self.IFF_button:
                        self.gameevents.add("release", "iff", type='EVENT_USER')
                    elif event.button == self.shots_button:
                        self.gameevents.add("release", "shots", type='EVENT_USER')
                    elif event.button == self.pnts_button:
                        self.gameevents.add("release", "pnts", type='EVENT_USER')

            else:

                if event.type == pygame.KEYDOWN:

                    if (pygame.key.get_mods() & self.modifier):
                        if event.key == pygame.K_q:
                            self.gameevents.add("press", "quit", type='EVENT_USER')

                    if event.key == pygame.K_RETURN:

                        if self.state == self.STATE_INTRO:
                            self.state = self.STATE_SETUP

                        elif self.state == self.STATE_SETUP:
                            self.state = self.STATE_GAMENO

                        elif self.state == self.STATE_GAMENO:
                            if self.mine_exists:
                                self.state = self.STATE_SETUP_IFF
                            else:
                                self.state = self.STATE_PREPARE

                        elif self.state == self.STATE_IFF:
                            self.state = self.STATE_PREPARE

                        elif self.state == self.STATE_SCORES:
                            self.state = self.STATE_SETUP

                    elif self.state == self.STATE_PLAY:

                        if event.key == self.thrust_key:
                            self.gameevents.add("press", "thrust", type='EVENT_USER')
                        elif event.key == self.left_turn_key:
                            self.gameevents.add("press", "left", type='EVENT_USER')
                        elif event.key == self.right_turn_key:
                            self.gameevents.add("press", "right", type='EVENT_USER')
                        elif event.key == self.fire_key:
                            self.gameevents.add("press", "fire", type='EVENT_USER')
                        elif event.key == self.IFF_key:
                            self.gameevents.add("press", "iff", type='EVENT_USER')
                        elif event.key == self.shots_key:
                            self.gameevents.add("press", "shots", type='EVENT_USER')
                        elif event.key == self.pnts_key:
                            self.gameevents.add("press", "pnts", type='EVENT_USER')
                        elif event.key == self.pause_key and self.config['General']['allow_pause']:
                                self.gameevents.add("press", "pause", type='EVENT_USER')
                                
                    elif self.state == self.STATE_PAUSED and event.key == self.pause_key:
                        self.gameevents.add("press", "unpause", type='EVENT_USER')
                                
                    else:
                        self.gameevents.add("press", event.key, "user", type='EVENT_SYSTEM')

                elif event.type == pygame.KEYUP:

                    if self.state == self.STATE_PLAY:

                        if event.key == self.thrust_key:
                            self.gameevents.add("release", "thrust", type='EVENT_USER')
                        elif event.key == self.left_turn_key:
                            self.gameevents.add("release", "left", type='EVENT_USER')
                        elif event.key == self.right_turn_key:
                            self.gameevents.add("release", "right", type='EVENT_USER')
                        elif event.key == self.fire_key:
                            self.gameevents.add("release", "fire", type='EVENT_USER')
                        elif event.key == self.IFF_key:
                            self.gameevents.add("release", "iff", type='EVENT_USER')
                        elif event.key == self.shots_key:
                            self.gameevents.add("release", "shots", type='EVENT_USER')
                        elif event.key == self.pnts_key:
                            self.gameevents.add("release", "pnts", type='EVENT_USER')

    def process_game_logic(self):
        """processes game logic to produce game events"""
        self.dmod = -1
        self.smod = -1
        if self.state == self.STATE_SETUP:
            if self.current_game < self.config['General']['games_per_session']:
                self.current_game += 1
                self.state = self.STATE_GAMENO
                self.game_title = "Game: %d of %d" % (self.current_game, self.config['General']['games_per_session'])
                self.game_title = pygl2d.font.RenderText(self.game_title, (255, 255, 0), self.f36)
                self.game_title_rect = self.game_title.get_rect()
                self.game_title_rect.center = (self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 16 * 7)
                self.gameevents.add("display_game", self.current_game)
            else:
                self.state = self.STATE_DONE
                self.ret = 0
                self.lc.stop()
        elif self.state == self.STATE_SETUP_IFF:
            self.mine_list.generate_foes()
            self.gameevents.add("display_foes", " ".join(self.mine_list.foe_letters), "player")
            self.foe_top = pygl2d.font.RenderText("The Type-2 mines for this session are:", (255, 255, 0), self.f24)
            self.foe_top_rect = self.foe_top.get_rect()
            self.foe_top_rect.center = (self.SCREEN_WIDTH / 2, 270 * self.aspect_ratio)
            self.foe_middle = pygl2d.font.RenderText(", ".join(self.mine_list.foe_letters), (255, 255, 255), self.f96)
            self.foe_middle_rect = self.foe_middle.get_rect()
            self.foe_middle_rect.center = (self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2)
            self.foe_midbot = pygl2d.font.RenderText("Try to memorize them before proceeding", (255, 255, 0), self.f24)
            self.foe_midbot_rect = self.foe_midbot.get_rect()
            self.foe_midbot_rect.center = (self.SCREEN_WIDTH / 2, 500 * self.aspect_ratio)
            self.foe_bottom = pygl2d.font.RenderText("Press return to begin", (255, 255, 0), self.f24)
            self.foe_bottom_rect = self.foe_bottom.get_rect()
            self.foe_bottom_rect.center = (self.SCREEN_WIDTH / 2, 600 * self.aspect_ratio)
            self.state = self.STATE_IFF
        elif self.state == self.STATE_PREPARE:
            self.gameevents.add("game", "ready", type='EVENT_SYSTEM')
            self.setup_world()
            self.state = self.STATE_PLAY
            self.gameevents.add("game", "start", type='EVENT_SYSTEM')
        elif self.state == self.STATE_PLAY:
            self.ship.compute()
            distance = self.ship.get_distance_to_point(self.WORLD_WIDTH / 2, self.WORLD_HEIGHT / 2)
            flight_max_inc = self.config['Score']['flight_max_increment']
            dmod = 1 - (distance - self.smallhex.radius * 1.125) / (self.WORLD_WIDTH / 2)
            if dmod > 1.0: dmod = 1.0
            if dmod < 0.0: dmod = 0.0
            smod = max([abs(self.ship.velocity.x), abs(self.ship.velocity.y)]) / self.ship.max_vel
            self.dmod = dmod
            self.smod = smod
            for missile in self.missile_list:
                missile.compute()
            if self.fortress_exists == True:
                self.fortress.compute()
            for shell in self.shell_list:
                shell.compute()
            if self.config['Hexagon']['hex_shrink']:
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
            if self.flighttimer.elapsed() > self.config['Score']['update_timer']:
                self.flighttimer.reset()
                def pointspace (a0, a1, a2, b0, b1, b2): return math.exp(a1 ** (a0 * a2)) * math.exp(b1 ** (b0 * b2))
                points = flight_max_inc * pointspace(self.dmod, 2, 1, self.smod, 2, 1.75) / pointspace(1, 2, 1, 1, 2, 1.75)
                self.gameevents.add("score+", "flight", points)
                self.flight2 += flight_max_inc * pointspace(self.dmod, 2, .45, self.smod, 2, 1) / pointspace(1, 2, .45, 1, 2, 1)
                if (self.ship.velocity.x ** 2 + self.ship.velocity.y ** 2) ** 0.5 < self.config['Score']['speed_threshold']:
                    self.gameevents.add("score+", "vlcty", self.config['Score']['VLCTY_increment'])
                    #self.gameevents.add("score+", "flight", self.config['Score']['VLCTY_increment'])
                else:
                    self.gameevents.add("score-", "vlcty", self.config['Score']['VLCTY_increment'])
                    #self.gameevents.add("score-", "flight", self.config['Score']['VLCTY_increment'])
                if self.bighex.collide(self.ship):
                    self.gameevents.add("score+", "cntrl", self.config['Score']['CNTRL_increment'])
                    #self.gameevents.add("score+", "flight", self.config['Score']['CNTRL_increment'])
                else:
                    self.gameevents.add("score+", "cntrl", self.config['Score']['CNTRL_increment'] / 2)
                    #self.gameevents.add("score+", "flight", self.config['Score']['CNTRL_increment']/2)
            if self.bonus_exists:
                if self.config['General']['bonus_system'] == "AX-CPT":
                    self.bonus.axcpt_update()
                else:
                    if self.bonus.visible == False and self.bonus.timer.elapsed() > self.config['Bonus']['symbol_down_time']:
                        self.gameevents.add("activate", "bonus")
                    elif self.bonus.visible == True and self.bonus.timer.elapsed() >= self.config['Bonus']['symbol_up_time']:
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

            if self.gametimer.elapsed() > self.config['General']['game_time']:
                self.gameevents.add("game", "over", type='EVENT_SYSTEM')
                self.state = self.STATE_SCORES

    def process_events(self):
        """processes internal list of game events for this frame"""
        gameevents = copy.copy(self.gameevents)
        del self.gameevents[:]
        while len(gameevents) > 0:
            currentevent = gameevents.pop(0)
            ticks = currentevent.ticks
            time = currentevent.time
            eid = currentevent.eid
            game = currentevent.game
            command = currentevent.command
            obj = currentevent.obj
            target = currentevent.target
            type = currentevent.type
            if self.config['Logging']['logging'] and currentevent.log:
                self.log.write("%s\t%f\t%d\t%d\t%d\t%s\t%s\t%s\n" % (type, time, ticks, game, eid, command, obj, target))
            if command == "press":
                if obj == "pause":
                    self.gametimer.pause()
                    self.state = self.STATE_PAUSED
                elif obj == "unpause":
                    self.state = self.STATE_PLAY
                    self.gametimer.unpause()
                elif obj == "quit":
                    self.lc.stop()
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
                    elif self.mine_list[0].tagged == "disable":
                        self.gameevents.add("tag", "already_disabled")
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
                        if (self.mine_list.iff_timer.elapsed() > self.config['Mine']['intrvl_min']) and (self.mine_list.iff_timer.elapsed() < self.config['Mine']['intrvl_max']):
                            self.gameevents.add("second_tag", "foe")
                        else:
                            self.gameevents.add("second_tag", "out_of_bounds")
                elif obj == "shots":
                    if not self.bonus_captured:
                        self.bonus_captured = True
                        if self.config['General']['bonus_system'] == "standard":
                            #if current symbol is bonus but previous wasn't, set flag to deny bonus if next symbol happens to be the bonus symbol
                            if (self.bonus.current_symbol == self.bonus.bonus_symbol) and (self.bonus.prior_symbol != self.bonus.bonus_symbol):
                                self.bonus.flag = True
                                self.gameevents.add("flagged_for_first_bonus")
                            if (self.bonus.current_symbol == self.bonus.bonus_symbol) and (self.bonus.prior_symbol == self.bonus.bonus_symbol):
                                #bonus available, check flag to award or deny bonus
                                if self.bonus.flag:
                                    self.gameevents.add("attempt_to_capture_flagged_bonus")
                                else:
                                    self.capturedBonuses += 1
                                    self.gameevents.add("shots_bonus_capture")
                                    self.gameevents.add("score+", "shots", self.config['Score']['bonus_missiles'])
                                    self.gameevents.add("score+", "bonus", self.config['Score']['bonus_points'] / 2)
                                    self.bonus.flag = True
                        else: #AX-CPT
                            if self.bonus.axcpt_flag == True and (self.bonus.state == "iti" or self.bonus.state == "target") and self.bonus.current_pair == "ax":
                                self.snd_bonus_success.play()
                                self.capturedBonuses += 1
                                self.gameevents.add("shots_bonus_capture")
                                self.gameevents.add("score+", "shots", self.config['Score']['bonus_missiles'])
                                if self.config['General']['next_gen']:
                                    self.gameevents.add("score+", "pnts", self.config['Score']['bonus_points'] / 2)
                                else:
                                    self.gameevents.add("score+", "bonus", self.config['Score']['bonus_points'] / 2)
                            elif self.bonus.axcpt_flag:
                                self.bonus.axcpt_flag = False
                                self.snd_bonus_fail.play()
                                self.gameevents.add("shots_bonus_failure")
                                if self.config['General']['next_gen']:
                                    self.gameevents.add("score-", "pnts", self.config['Score']['bonus_points'] / 2)
                                else:
                                    self.gameevents.add("score-", "bonus", self.config['Score']['bonus_points'] / 2)
                elif obj == "pnts":
                    if not self.bonus_captured:
                        self.bonus_captured = True
                        if self.config['General']['bonus_system'] == "standard":
                        #if current symbol is bonus but previous wasn't, set flag to deny bonus if next symbol happens to be the bonus symbol
                            if (self.bonus.current_symbol == self.bonus.bonus_symbol) and (self.bonus.prior_symbol != self.bonus.bonus_symbol):
                                self.bonus.flag = True
                                self.gameevents.add("flagged_for_first_bonus")
                            if (self.bonus.current_symbol == self.bonus.bonus_symbol) and (self.bonus.prior_symbol == self.bonus.bonus_symbol):
                                #bonus available, check flag to award or deny bonus
                                if self.bonus.flag:
                                    self.gameevents.add("attempt_to_capture_flagged_bonus")
                                else:
                                    self.capturedBonuses += 1
                                    self.gameevents.add("pnts_pnts_capture")
                                    self.gameevents.add("score+", "bonus", self.config['Score']['bonus_points'])
                                    self.gameevents.add("score+", "pnts", self.config['Score']['bonus_points'])
                                    self.bonus.flag = True
                        else: #AX-CPT
                            if self.bonus.axcpt_flag == True and (self.bonus.state == "iti" or self.bonus.state == "target") and self.bonus.current_pair == "ax":
                                self.snd_bonus_success.play()
                                self.capturedBonuses += 1
                                self.gameevents.add("pnts_bonus_capture")
                                if self.config['General']['next_gen']:
                                    self.gameevents.add("score+", "pnts", self.config['Score']['bonus_points'])
                                else:
                                    self.gameevents.add("score+", "pnts", self.config['Score']['bonus_points'])
                                    self.gameevents.add("score+", "bonus", self.config['Score']['bonus_points'])
                            elif self.bonus.axcpt_flag:
                                self.bonus.axcpt_flag = False
                                self.snd_bonus_fail.play()
                                self.gameevents.add("pnts_bonus_failure")
                                if self.config['General']['next_gen']:
                                    self.gameevents.add("score-", "pnts", self.config['Score']['bonus_points'] / 2)
                                else:
                                    self.gameevents.add("score-", "bonus", self.config['Score']['bonus_points'] / 2)
            elif command == "destroyed":
                if obj == "ship":
                    self.deaths += 1
                    self.reset_position()
                    self.reset_mines()
            elif command == "bonus_available":
                self.totalBonuses += 1
            elif command == "first_tag":
                if obj == "foe":
                    self.mine_list.iff_flag = True
                    self.mine_list.iff_timer.reset()
                elif len(self.mine_list) > 0:
                    self.mine_list[0].tagged = "fail"
            elif command == "second_tag":
                self.mine_list.iff_flag = False
                if obj == "foe" and len(self.mine_list) > 0:
                    self.mine_list[0].tagged = "tagged"
            elif command == "release":
                if obj == "left":
                    self.ship.turn_left_flag = False
                elif obj == "right":
                    self.ship.turn_right_flag = False
                elif obj == "thrust":
                    self.ship.thrust_flag = False
            elif command == "warp":
                self.gameevents.add("score-", "pnts", self.config['Score']['warp_penalty'])
                self.gameevents.add("score-", "flight", self.config['Score']['warp_penalty'])
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
                self.totalMines += 1
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
                self.gameevents.add("score-", "mines", self.config['Score']['mine_timeout_penalty'])
            elif command == "score++":
                if obj == "bonus_points":
                    self.gameevents.add("score+", "pnts", int(target))
            elif command == "score+":
                self.score.__setattr__(obj, self.score.__getattribute__(obj) + float(target))
                if self.score.shots > self.config['Missile']['missile_max']:
                    self.score.shots = self.config['Missile']['missile_max']
            elif command == "score-":
                self.score.__setattr__(obj, self.score.__getattribute__(obj) - float(target))
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
            self.gameevents.add("score-", "pnts", self.config['Score']['small_hex_penalty'])
            self.gameevents.add("score-", "flight", self.config['Score']['small_hex_penalty'])
            self.smallhex.small_hex_flag = True
        elif obj == "shell":
            #remove shell, target is index of shell in shell_list
            del self.shell_list[target]
            self.gameevents.add("score-", "pnts", self.config['Score']['shell_hit_penalty'])
            self.gameevents.add("score-", "fortress", self.config['Score']['shell_hit_penalty'])
            self.ship.take_damage()
            if not self.ship.alive:
                self.gameevents.add("destroyed", "ship", "shell")
                self.gameevents.add("score-", "pnts", self.config['Score']['ship_death_penalty'])
                self.gameevents.add("score-", "fortress", self.config['Score']['ship_death_penalty'])
                self.ship.color = (255, 255, 0)
            elif self.config['Ship']['colored_damage']:
                g = 255 / self.ship.start_health * (self.ship.health - 1)
                self.ship.color = (255, g, 0)

        elif obj.startswith("missile_"):
            #if missile hits fortress, need to check if it takes damage when mine is onscreen
            if target == "fortress" and (len(self.mine_list) == 0 or self.config['Fortress']['hit_fortress_while_mine']):
                if self.ship.shot_timer.elapsed() >= self.config['Fortress']['vlner_time']:
                    self.gameevents.add("score+", "vlner", 1)
                if self.ship.shot_timer.elapsed() < self.config['Fortress']['vlner_time'] and self.score.vlner >= self.config['Fortress']['vlner_threshold']:
                    self.gameevents.add("destroyed", "fortress")
                    self.fortress.alive = False
                    #r = choice([0,45,90,135,180,225,270,315])
                    #if r:
                    #    self.explosion.rotate(r)
                    self.fortress.reset_timer.reset()
                    self.snd_explosion.play()
                    self.gameevents.add("score+", "pnts", self.config['Score']['destroy_fortress'])
                    self.gameevents.add("score+", "fortress", self.config['Score']['destroy_fortress'])
                    self.score.vlner = 0
                    self.destroyedFortresses += 1
                    self.gameevents.add("reset", "VLNER")
                    #do we reset the mine timer?
                    if self.config['Mine']['fortress_resets_mine']:
                        self.mine_list.timer.reset()
                        self.mine_list.flag = False
                elif self.ship.shot_timer.elapsed() < self.config['Fortress']['vlner_time'] and self.score.vlner < self.config['Fortress']['vlner_threshold']:
                    self.gameevents.add("reset", "VLNER")
                    self.score.vlner = 0
                    self.snd_vlner_reset.play()
                self.ship.shot_timer.reset()
            elif target.startswith("mine_"):
                #deal with missile hitting mine
                #can the mine be hit?
                if len(self.mine_list) > 0:
                    if self.mine_list[0].tagged == "fail":
                        self.gameevents.add("collide", "fail_tagged_mine")
                    elif self.mine_list[0].tagged == "disabled":
                        self.gameevents.add("collide", "disable_tagged_mine")
                    elif self.mine_list[0].tagged == "untagged":
                        if self.score.iff in self.mine_list.foe_letters:
                            self.mine_list[0].tagged = "disable"
                            self.gameevents.add("collide", "untagged_foe_mine")
                        else:
                            self.gameevents.add("collide", "friend_mine")
                    elif self.mine_list[0].tagged == "tagged" and self.score.iff in self.mine_list.foe_letters:
                        self.gameevents.add("collide", "tagged_foe_mine")
        elif obj.startswith("mine_"):
            #mine hit the ship
            index = int(obj[-1])
            #check to see if mine is still alive, it is possible to shot and
            #collide with a mine at the same time, ties go to ship
            if index < len(self.mine_list):
                del self.mine_list[index]
                self.score.iff = ''
                self.score.intrvl = 0
                self.mine_list.flag = False
                self.mine_list.iff_flag = False
                self.mine_list.timer.reset()
                self.gameevents.add("score-", "pnts", self.config['Score']['mine_hit_penalty'])
                self.gameevents.add("score-", "mines", self.config['Score']['mine_hit_penalty'])
                self.mine2 -= self.config['Score']['mine_hit_penalty']
                self.ship.take_damage()
                if not self.ship.alive:
                    self.gameevents.add("destroyed", "ship", "mine")
                    self.gameevents.add("score-", "pnts", self.config['Score']['ship_death_penalty'])
                    self.gameevents.add("score-", "mines", self.config['Score']['ship_death_penalty'])
                    self.mine2 -= self.config['Score']['ship_death_penalty']
                    self.ship.color = (255, 255, 0)
                elif self.config['Ship']['colored_damage']:
                    g = 255 / self.ship.start_health * (self.ship.health - 1)
                    self.ship.color = (255, g, 0)
        elif obj == "friend_mine":
            #get rid of mine
            self.destroyedMines += 1
            self.mine_list.flag = False
            self.mine_list.iff_flag = False
            self.gameevents.add("score+", "mines", self.config['Score']['energize_friend'])
            self.gameevents.add("score+", "pnts", self.config['Score']['energize_friend'])
            #see how long mine has been alive. 0-100 points if destroyed within 10 seconds
            self.gameevents.add("score+", "mines", 100 - 10 * math.floor(self.mine_list.timer.elapsed() / 1000))
            self.gameevents.add("score+", "speed", 100 - 10 * math.floor(self.mine_list.timer.elapsed() / 1000))
            #print self.mine_list.timer.elapsed()
            #print 100 - 10 * math.floor(self.mine_list.timer.elapsed()/1000)
            self.mine_list.timer.reset()
            self.mine2 += 50
            #amazingly, missile can hit the mine in the same frame as the mine hits the ship
            if len(self.mine_list) > 0:
                del self.mine_list[0]
            self.score.iff = ''
            self.score.intrvl = 0
        elif obj == "tagged_foe_mine":
            #get rid of mine
            self.destroyedMines += 1
            self.mine_list.flag = False
            self.mine_list.iff_flag = False
            self.gameevents.add("score+", "mines", self.config['Score']['destroy_foe'])
            self.gameevents.add("score+", "pnts", self.config['Score']['destroy_foe'])
            #see how long mine has been alive. 0-100 points if destroyed within 10 seconds
            self.gameevents.add("score+", "mines", 100 - 10 * math.floor(self.mine_list.timer.elapsed() / 1000))
            self.gameevents.add("score+", "speed", 100 - 10 * math.floor(self.mine_list.timer.elapsed() / 1000))
            self.mine_list.timer.reset()
            self.mine2 += 75
            if len(self.mine_list) > 0:
                del self.mine_list[0]
            self.score.iff = ''
            self.score.intrvl = 0

    def reset_mines(self):
        del self.mine_list[:]
        self.mine_list.flag = False
        self.mine_list.iff_flag = False
        self.mine_list.timer.reset()

    def test_collisions(self):
        """test collisions between relevant game entities"""
        if self.fortress_exists:
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
                self.gameevents.add("collide", "missile_" + str(i), "fortress")
                del_missile = True
            for j, mine in enumerate(self.mine_list):
                if missile.collide(mine) and not missile.collide(self.fortress):
                    self.gameevents.add("collide", "missile_" + str(i), "mine_" + str(j))
                    del_missile = True
            if del_missile:
                del self.missile_list[i]
        for i, mine in enumerate(self.mine_list):
            if mine.collide(self.ship):
                self.gameevents.add("collide", "mine_" + str(i), "ship")

    def check_bounds(self):
        """determine whether any shells or missiles have left the world"""
        for i, missile in enumerate(self.missile_list):
            if missile.out_of_bounds(self.world):
                del self.missile_list[i]
                self.gameevents.add("bounds_remove", "missile")
        for i, shell in enumerate(self.shell_list):
            if shell.out_of_bounds(self.world):
                del self.shell_list[i]
                self.gameevents.add("bounds_remove", "shell")


    def reset_position(self):
        """pauses the game and resets"""
        self.snd_explosion.play()
        pygame.time.delay(1000)
        self.score.iff = ""
        self.ship.alive = True
        self.ship.position.x = self.world.left + self.config['Ship']['ship_pos_x'] * self.aspect_ratio
        self.ship.position.y = self.world.top + self.config['Ship']['ship_pos_y'] * self.aspect_ratio
        self.ship.velocity.x = self.config['Ship']['ship_vel_x']
        self.ship.velocity.y = self.config['Ship']['ship_vel_y']
        self.ship.orientation = self.config['Ship']['ship_orientation']

    def draw_stars(self):
        stars = [[], [], []]
        for star in self.stars:
            if self.state == self.STATE_PLAY:
                star[0] += star[2] * self.star_velocty_x
                star[1] += star[2] * self.star_velocty_y
                if star[0] >= self.world.right - self.linewidth:
                    star[0] = self.world.left + self.linewidth
                    star[1] = randrange(self.world.top + self.linewidth, self.world.bottom - self.linewidth)
                    star[2] = choice([1, 2, 3])
                elif star[0] <= self.world.left + self.linewidth:
                    star[0] = self.world.right - self.linewidth
                    star[1] = randrange(self.world.top + self.linewidth, self.world.bottom - self.linewidth)
                    star[2] = choice([1, 2, 3])
                elif star[1] >= self.world.bottom - self.linewidth:
                    star[1] = self.world.top + self.linewidth
                    star[0] = randrange(self.world.left + self.linewidth, self.world.right - self.linewidth)
                    star[2] = choice([1, 2, 3])
                elif star[1] <= self.world.top + self.linewidth:
                    star[1] = self.world.bottom - self.linewidth
                    star[0] = randrange(self.world.left + self.linewidth, self.world.right - self.linewidth)
                    star[2] = choice([1, 2, 3])
            stars[star[2] - 1].append((star[0], star[1]))
        pygl2d.draw.points2(stars[0], (100, 100, 100), 1)
        pygl2d.draw.points2(stars[1], (190, 190, 190), 2)
        pygl2d.draw.points2(stars[2], (255, 255, 255), 3)

    def draw_world(self):       
        if self.config['Graphics']['max_stars']:
            self.draw_stars()
            
        if not self.config['Hexagon']['hide_big_hex']:
            self.bighex.draw()
        if self.fortress_exists and not self.fortress.alive:
            pass
        else:
            if not self.config['Hexagon']['hide_small_hex']:
                self.smallhex.draw()
        
        for shell in self.shell_list:
            shell.draw()
        if self.fortress_exists:
            if self.fortress.alive:
                self.fortress.draw()
            else:
                self.explosion_rect.center = (self.fortress.position.x, self.fortress.position.y)
                self.explosion.draw(self.explosion_rect.topleft)
        for missile in self.missile_list:
            missile.draw()
        if self.ship.alive:
            self.ship.draw()
        else:
            self.explosion_small_rect.center = (self.ship.position.x, self.ship.position.y)
            self.explosion_small.draw(self.explosion_small_rect.topleft)
        self.mine_list.draw()
        if self.bonus_exists and self.bonus.visible:
            self.bonus.draw()

    def draw(self):
        """draws the world"""
        
        pygl2d.display.begin_draw(self.screen_size)
        
        if self.state == self.STATE_INTRO:
            self.draw_intro()
            
        elif self.state == self.STATE_GAMENO:
            self.draw_game_number()
            
        elif self.state == self.STATE_IFF:
            self.draw_foe_mines()
            
        elif self.state == self.STATE_PLAY or self.state == self.STATE_PAUSED:
            if self.state == self.STATE_PAUSED and self.config['Display']['pause_overlay']:
                self.draw_pause_overlay()            
            else:
                pygl2d.draw.polygon([self.screen_rect.topleft, self.screen_rect.topright, self.screen_rect.bottomright, self.screen_rect.bottomleft], (64, 64, 64), stipple_pattern=self.happy[::-1])
                self.frame.draw()
                self.score.draw()
                with scissor_box(self.world):
                    self.draw_world()

        elif self.state == self.STATE_SCORES:
            self.draw_scores()

        self.gameevents.add("display", 'preflip', 'main', False, type='EVENT_SYSTEM')
        
        pygl2d.display.end_draw()

    def log_world(self):
        """logs current state of world to logfile"""
        system_time = get_time()
        game_time = pygame.time.get_ticks()
        if self.state == 2:
            smod = self.smod
            dmod = self.dmod
        else:
            smod = "NA"
            dmod = "NA"
        if self.ship and self.ship.alive:
            ship_alive = "y"
            ship_x = "%.3f" % (self.ship.position.x)
            ship_y = "%.3f" % (self.ship.position.y)
            ship_vel_x = "%.3f" % (self.ship.velocity.x)
            ship_vel_y = "%.3f" % (self.ship.velocity.y)
            ship_orientation = "%.3f" % (self.ship.orientation)
            ship_health = str(self.ship.health)
            distance = str(self.ship.get_distance_to_point(self.WORLD_WIDTH / 2, self.WORLD_HEIGHT / 2))
        else:
            ship_alive = "n"
            ship_x = "NA"
            ship_y = "NA"
            ship_vel_x = "NA"
            ship_vel_y = "NA"
            ship_orientation = "NA"
            ship_health = "NA"
            distance = "NA"
        if len(self.mine_list) > 0:
            mine_no = self.mine_list.mine_count
            mine_id = self.mine_list[0].iff
        else:
            mine_no = "NA"
            mine_id = "NA"
        if self.fortress and self.fortress_exists and self.fortress.alive:
            fortress_alive = "y"
            fortress_orientation = str(self.fortress.orientation)
            fortress_x = str(self.fortress.position.x)
            fortress_y = str(self.fortress.position.y)
        else:
            fortress_alive = "n"
            fortress_orientation = "NA"
            fortress_x = "NA"
            fortress_y = "NA"
        if self.bonus and self.config['General']['bonus_system'] == "AX-CPT":
            bonus_isi = str(self.bonus.isi_time)
        else:
            bonus_isi = 'NA'
        if self.bonus and self.bonus.visible:
            bonus_no = self.bonus.bonus_count
            bonus_cur_x = self.bonus.position.x
            bonus_cur_y = self.bonus.position.y
        else:
            bonus_no = "NA"
            bonus_cur_x = "NA"
            bonus_cur_y = "NA"
        if not self.bonus or self.bonus.current_symbol == '':
            bonus_cur = "NA"
        else:
            bonus_cur = self.bonus.current_symbol
        if not self.bonus or self.bonus.prior_symbol == '':
            bonus_prev = "NA"
        else:
            bonus_prev = self.bonus.prior_symbol
        if not self.score and self.score.iff == '':
            iff_score = 'NA'
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

        data = ["STATE", system_time, game_time, self.current_game, "NA", "NA", "NA", "NA",
                " ".join(self.mine_list.foe_letters), ship_alive, ship_health, ship_x, ship_y,
                smod, dmod, ship_vel_x, ship_vel_y, ship_orientation, distance, mine_no, mine_id,
                self.mine_list, fortress_alive, fortress_x, fortress_y, fortress_orientation,
                self.missile_list, self.shell_list]

        if self.config['General']['bonus_system'] == "AX-CPT":
            data = data + [ bonus_no, bonus_prev, bonus_cur, bonus_cur_x, bonus_cur_y, bonus_isi ]
        else:
            data = data + [ bonus_no, bonus_prev, bonus_cur, bonus_cur_x, bonus_cur_y ]

        data = data + [self.score.pnts, self.score.cntrl, self.score.vlcty,
                       self.score.vlner, iff_score, self.score.intrvl, self.score.speed,
                       self.score.shots, self.score.flight, self.flight2, self.score.fortress,
                       self.score.mines, self.mine2, self.score.bonus, thrust_key, left_key,
                       right_key, fire_key, iff_key, shots_key, pnts_key]

        for name in self.plugins:
            if hasattr(self.plugins[name], "logCallback"):
                data = data + self.plugins[name].logCallback()

        self.log.write("\t".join(map(str, data)) + "\n")

    def draw_intro(self):
        """display intro scene"""
        self.intro_title.draw(self.intro_title_rect.topleft)
        self.intro_vers.draw(self.intro_vers_rect.topleft)
        self.intro_copy.draw(self.intro_copy_rect.topleft)
        self.intro_logo.draw(self.intro_logo_rect.topleft)

    def draw_game_number(self):
        """before game begins, present the game number"""        
        self.game_title.draw(self.game_title_rect.topleft)
        pygl2d.draw.line((self.SCREEN_WIDTH / 4 , self.SCREEN_HEIGHT / 16 * 8.5), (self.SCREEN_WIDTH / 4 * 3, self.SCREEN_HEIGHT / 16 * 8.5), (255, 255, 255))
        pygl2d.draw.line((self.SCREEN_WIDTH / 4 , self.SCREEN_HEIGHT / 16 * 5.5), (self.SCREEN_WIDTH / 4 * 3, self.SCREEN_HEIGHT / 16 * 5.5), (255, 255, 255))
        
    def draw_foe_mines(self):
        """before game begins, present the list of IFF letters to target"""
        self.foe_top.draw(self.foe_top_rect.topleft)
        self.foe_middle.draw(self.foe_middle_rect.topleft)
        self.foe_midbot.draw(self.foe_midbot_rect.topleft)
        self.foe_bottom.draw(self.foe_bottom_rect.topleft)

    def draw_old_score(self):
        """shows score for last game and waits to continue"""
        pygame.event.get() #clear event list? Otherwise it skips
        self.screen.fill((0, 0, 0))
        gamesurf = self.f36.render("Game %d" % (self.current_game), True, (255, 255, 0))
        gamerect = gamesurf.get_rect()
        gamerect.centery = self.SCREEN_HEIGHT / 16 * 2
        gamerect.centerx = self.SCREEN_WIDTH / 2
        self.screen.blit(gamesurf, gamerect)
        pygame.draw.line(self.screen, (255, 255, 255), (self.SCREEN_WIDTH / 4 , self.SCREEN_HEIGHT / 16 * 3), (self.SCREEN_WIDTH / 4 * 3, self.SCREEN_HEIGHT / 16 * 3))
        pntssurf = self.f24.render("PNTS score:", True, (255, 255, 0))
        pntsrect = pntssurf.get_rect()
        pntsrect.left = self.SCREEN_WIDTH / 3
        pntsrect.centery = self.SCREEN_HEIGHT / 16 * 4
        self.screen.blit(pntssurf, pntsrect)
        cntrlsurf = self.f24.render("CNTRL score:", True, (255, 255, 0))
        cntrlrect = cntrlsurf.get_rect()
        cntrlrect.left = self.SCREEN_WIDTH / 3
        cntrlrect.centery = self.SCREEN_HEIGHT / 16 * 6
        self.screen.blit(cntrlsurf, cntrlrect)
        vlctysurf = self.f24.render("VLCTY score:", True, (255, 255, 0))
        vlctyrect = vlctysurf.get_rect()
        vlctyrect.left = self.SCREEN_WIDTH / 3
        vlctyrect.centery = self.SCREEN_HEIGHT / 16 * 8
        self.screen.blit(vlctysurf, vlctyrect)
        speedsurf = self.f24.render("SPEED score:", True, (255, 255, 0))
        speedrect = speedsurf.get_rect()
        speedrect.left = self.SCREEN_WIDTH / 3
        speedrect.centery = self.SCREEN_HEIGHT / 16 * 10
        self.screen.blit(speedsurf, speedrect)
        pntsnsurf = self.f24.render("%d" % self.score.pnts, True, (255, 255, 255))
        pntsnrect = pntsnsurf.get_rect()
        pntsnrect.right = self.SCREEN_WIDTH / 3 * 2
        pntsnrect.centery = self.SCREEN_HEIGHT / 16 * 4
        self.screen.blit(pntsnsurf, pntsnrect)
        cntrlnsurf = self.f24.render("%d" % self.score.cntrl, True, (255, 255, 255))
        cntrlnrect = cntrlnsurf.get_rect()
        cntrlnrect.right = self.SCREEN_WIDTH / 3 * 2
        cntrlnrect.centery = self.SCREEN_HEIGHT / 16 * 6
        self.screen.blit(cntrlnsurf, cntrlnrect)
        vlctynsurf = self.f24.render("%d" % self.score.vlcty, True, (255, 255, 255))
        vlctynrect = vlctynsurf.get_rect()
        vlctynrect.right = self.SCREEN_WIDTH / 3 * 2
        vlctynrect.centery = self.SCREEN_HEIGHT / 16 * 8
        self.screen.blit(vlctynsurf, vlctynrect)
        speednsurf = self.f24.render("%d" % self.score.speed, True, (255, 255, 255))
        speednrect = speednsurf.get_rect()
        speednrect.right = self.SCREEN_WIDTH / 3 * 2
        speednrect.centery = self.SCREEN_HEIGHT / 16 * 10
        self.screen.blit(speednsurf, speednrect)
        #draw line
        pygame.draw.line(self.screen, (255, 255, 255), (self.SCREEN_WIDTH / 4 , self.SCREEN_HEIGHT / 16 * 11), (self.SCREEN_WIDTH / 4 * 3, self.SCREEN_HEIGHT / 16 * 11))
        totalsurf = self.f24.render("Total game score:", True, (255, 255, 0))
        totalrect = totalsurf.get_rect()
        totalrect.left = self.SCREEN_WIDTH / 3
        totalrect.centery = self.SCREEN_HEIGHT / 16 * 12
        self.screen.blit(totalsurf, totalrect)
        totalnsurf = self.f24.render("%d" % (self.score.pnts + self.score.cntrl + self.score.vlcty + self.score.speed), True, (255, 255, 255))
        totalnrect = totalnsurf.get_rect()
        totalnrect.right = self.SCREEN_WIDTH / 3 * 2
        totalnrect.centery = self.SCREEN_HEIGHT / 16 * 12
        self.screen.blit(totalnsurf, totalnrect)
        if self.current_game == self.config['General']['games_per_session']:
            finalsurf = self.f24.render("You're done! Press return to exit", True, (0, 255, 0))
        else:
            finalsurf = self.f24.render("Press return for next game", True, (0, 255, 0))
        finalrect = finalsurf.get_rect()
        finalrect.centerx = self.SCREEN_WIDTH / 2
        finalrect.centery = self.SCREEN_HEIGHT / 16 * 14
        self.screen.blit(finalsurf, finalrect)

    def draw_ng_score(self, time):
        pygame.event.get() #clear event list? Otherwise it skips
        self.screen.fill((0, 0, 0))
        gamesurf = self.f36.render("Game %d Stats" % (self.current_game), True, (255, 255, 0))
        gamerect = gamesurf.get_rect()
        gamerect.centery = self.SCREEN_HEIGHT / 16 * 2
        gamerect.centerx = self.SCREEN_WIDTH / 2
        self.screen.blit(gamesurf, gamerect)
        pygame.draw.line(self.screen, (255, 255, 255), (self.SCREEN_WIDTH / 4 , self.SCREEN_HEIGHT / 16 * 3), (self.SCREEN_WIDTH / 4 * 3, self.SCREEN_HEIGHT / 16 * 3))
        pntssurf = self.f24.render("Points:", True, (255, 255, 0))
        pntsrect = pntssurf.get_rect()
        pntsrect.left = self.SCREEN_WIDTH / 3
        pntsrect.centery = self.SCREEN_HEIGHT / 16 * 4
        self.screen.blit(pntssurf, pntsrect)
        pntsnsurf = self.f24.render("%d" % self.score.pnts, True, (255, 255, 255))
        pntsnrect = pntsnsurf.get_rect()
        pntsnrect.right = self.SCREEN_WIDTH / 3 * 2
        pntsnrect.centery = self.SCREEN_HEIGHT / 16 * 4
        self.screen.blit(pntsnsurf, pntsnrect)
        deathsurf = self.f24.render("Deaths:", True, (255, 255, 0))
        deathrect = deathsurf.get_rect()
        deathrect.left = self.SCREEN_WIDTH / 3
        deathrect.centery = self.SCREEN_HEIGHT / 16 * 5.5
        self.screen.blit(deathsurf, deathrect)
        deathnsurf = self.f24.render("%d" % (self.deaths), True, (255, 255, 255))
        deathnrect = deathnsurf.get_rect()
        deathnrect.right = self.SCREEN_WIDTH / 3 * 2
        deathnrect.centery = self.SCREEN_HEIGHT / 16 * 5.5
        self.screen.blit(deathnsurf, deathnrect)
        cntrlsurf = self.f24.render("Destroyed fortresses:", True, (255, 255, 0))
        cntrlrect = cntrlsurf.get_rect()
        cntrlrect.left = self.SCREEN_WIDTH / 3
        cntrlrect.centery = self.SCREEN_HEIGHT / 16 * 7
        self.screen.blit(cntrlsurf, cntrlrect)
        cntrlnsurf = self.f24.render("%d" % (self.destroyedFortresses), True, (255, 255, 255))
        cntrlnrect = cntrlnsurf.get_rect()
        cntrlnrect.right = self.SCREEN_WIDTH / 3 * 2
        cntrlnrect.centery = self.SCREEN_HEIGHT / 16 * 7
        self.screen.blit(cntrlnsurf, cntrlnrect)
        vlctysurf = self.f24.render("Destroyed mines:", True, (255, 255, 0))
        vlctyrect = vlctysurf.get_rect()
        vlctyrect.left = self.SCREEN_WIDTH / 3
        vlctyrect.centery = self.SCREEN_HEIGHT / 16 * 8.5
        self.screen.blit(vlctysurf, vlctyrect)
        vlctynsurf = self.f24.render("%d of %d" % (self.destroyedMines, self.totalMines), True, (255, 255, 255))
        vlctynrect = vlctynsurf.get_rect()
        vlctynrect.right = self.SCREEN_WIDTH / 3 * 2
        vlctynrect.centery = self.SCREEN_HEIGHT / 16 * 8.5
        self.screen.blit(vlctynsurf, vlctynrect)
        speedsurf = self.f24.render("Captured bonuses:", True, (255, 255, 0))
        speedrect = speedsurf.get_rect()
        speedrect.left = self.SCREEN_WIDTH / 3
        speedrect.centery = self.SCREEN_HEIGHT / 16 * 10
        self.screen.blit(speedsurf, speedrect)
        speednsurf = self.f24.render("%d of %d" % (self.capturedBonuses, self.totalBonuses), True, (255, 255, 255))
        speednrect = speednsurf.get_rect()
        speednrect.right = self.SCREEN_WIDTH / 3 * 2
        speednrect.centery = self.SCREEN_HEIGHT / 16 * 10
        self.screen.blit(speednsurf, speednrect)
        pygame.draw.line(self.screen, (255, 255, 255), (self.SCREEN_WIDTH / 4 , self.SCREEN_HEIGHT / 16 * 11), (self.SCREEN_WIDTH / 4 * 3, self.SCREEN_HEIGHT / 16 * 11))
        if self.current_game == self.config['General']['games_per_session']:
            finalsurf = self.f24.render("You're done! Press return to exit", True, (0, 255, 0))
        else:
            finalsurf = self.f24.render("Press return for next game", True, (0, 255, 0))
        finalrect = finalsurf.get_rect()
        finalrect.centerx = self.SCREEN_WIDTH / 2
        finalrect.centery = self.SCREEN_HEIGHT / 16 * 14
        self.screen.blit(finalsurf, finalrect)

    def draw_new_score(self):
        """shows score for last game and waits to continue"""
        pygame.event.get() #clear event list? Otherwise it skips
        self.screen.fill((0, 0, 0))
        #sessionsurf = self.f24.render("Session %d, Game %d/%s"%(self.session_number, self.game_number, self.config["games_per_session"]), True, (255,255,255))
        # sessionrect = sessionsurf.get_rect()
        # sessionrect.centerx = self.SCREEN_WIDTH / 2
        # sessionrect.y = 100
        # self.screen.blit(sessionsurf, sessionrect)
        gamesurf = self.f36.render("Game %d" % (self.current_game), True, (255, 255, 0))
        gamerect = gamesurf.get_rect()
        gamerect.centery = self.SCREEN_HEIGHT / 16 * 2
        gamerect.centerx = self.SCREEN_WIDTH / 2
        self.screen.blit(gamesurf, gamerect)
        pygame.draw.line(self.screen, (255, 255, 255), (self.SCREEN_WIDTH / 4 , self.SCREEN_HEIGHT / 16 * 3), (self.SCREEN_WIDTH / 4 * 3, self.SCREEN_HEIGHT / 16 * 3))
        pntssurf = self.f24.render("Flight score:", True, (255, 255, 0))
        pntsrect = pntssurf.get_rect()
        pntsrect.left = self.SCREEN_WIDTH / 3
        pntsrect.centery = self.SCREEN_HEIGHT / 16 * 4
        self.screen.blit(pntssurf, pntsrect)
        cntrlsurf = self.f24.render("Fortress score:", True, (255, 255, 0))
        cntrlrect = cntrlsurf.get_rect()
        cntrlrect.left = self.SCREEN_WIDTH / 3
        cntrlrect.centery = self.SCREEN_HEIGHT / 16 * 6
        self.screen.blit(cntrlsurf, cntrlrect)
        vlctysurf = self.f24.render("Mine score:", True, (255, 255, 0))
        vlctyrect = vlctysurf.get_rect()
        vlctyrect.left = self.SCREEN_WIDTH / 3
        vlctyrect.centery = self.SCREEN_HEIGHT / 16 * 8
        self.screen.blit(vlctysurf, vlctyrect)
        speedsurf = self.f24.render("Bonus score:", True, (255, 255, 0))
        speedrect = speedsurf.get_rect()
        speedrect.left = self.SCREEN_WIDTH / 3
        speedrect.centery = self.SCREEN_HEIGHT / 16 * 10
        self.screen.blit(speedsurf, speedrect)
        pntsnsurf = self.f24.render("%d" % self.score.flight, True, (255, 255, 255))
        pntsnrect = pntsnsurf.get_rect()
        pntsnrect.right = self.SCREEN_WIDTH / 3 * 2
        pntsnrect.centery = self.SCREEN_HEIGHT / 16 * 4
        self.screen.blit(pntsnsurf, pntsnrect)
        cntrlnsurf = self.f24.render("%d" % self.score.fortress, True, (255, 255, 255))
        cntrlnrect = cntrlnsurf.get_rect()
        cntrlnrect.right = self.SCREEN_WIDTH / 3 * 2
        cntrlnrect.centery = self.SCREEN_HEIGHT / 16 * 6
        self.screen.blit(cntrlnsurf, cntrlnrect)
        vlctynsurf = self.f24.render("%d" % self.score.mines, True, (255, 255, 255))
        vlctynrect = vlctynsurf.get_rect()
        vlctynrect.right = self.SCREEN_WIDTH / 3 * 2
        vlctynrect.centery = self.SCREEN_HEIGHT / 16 * 8
        self.screen.blit(vlctynsurf, vlctynrect)
        speednsurf = self.f24.render("%d" % self.score.bonus, True, (255, 255, 255))
        speednrect = speednsurf.get_rect()
        speednrect.right = self.SCREEN_WIDTH / 3 * 2
        speednrect.centery = self.SCREEN_HEIGHT / 16 * 10
        self.screen.blit(speednsurf, speednrect)
        #draw line
        pygame.draw.line(self.screen, (255, 255, 255), (self.SCREEN_WIDTH / 4 , self.SCREEN_HEIGHT / 16 * 11), (self.SCREEN_WIDTH / 4 * 3, self.SCREEN_HEIGHT / 16 * 11))
        totalsurf = self.f24.render("Total game score:", True, (255, 255, 0))
        totalrect = totalsurf.get_rect()
        totalrect.left = self.SCREEN_WIDTH / 3
        totalrect.centery = self.SCREEN_HEIGHT / 16 * 12
        self.screen.blit(totalsurf, totalrect)
        totalnsurf = self.f24.render("%d" % (self.score.flight + self.score.fortress + self.score.mines + self.score.bonus), True, (255, 255, 255))
        totalnrect = totalnsurf.get_rect()
        totalnrect.right = self.SCREEN_WIDTH / 3 * 2
        totalnrect.centery = self.SCREEN_HEIGHT / 16 * 12
        self.screen.blit(totalnsurf, totalnrect)
        if self.current_game == self.config['General']['games_per_session']:
            finalsurf = self.f24.render("You're done! Press return to exit", True, (0, 255, 0))
        else:
            finalsurf = self.f24.render("Press return for next game", True, (0, 255, 0))
        finalrect = finalsurf.get_rect()
        finalrect.centerx = self.SCREEN_WIDTH / 2
        finalrect.centery = self.SCREEN_HEIGHT / 16 * 14
        self.screen.blit(finalsurf, finalrect)

    def init_stars(self):
        """ Create the starfield """
        self.stars = []
        for i in range(self.config['Graphics']['max_stars']):
            star = [randrange(self.world.left, self.world.right),
                    randrange(self.world.top, self.world.bottom),
                    choice([1, 2, 3])]
            self.stars.append(star)

    def draw_kp(self):

        color = (48, 48, 48)

        left = self.WORLD_WIDTH / 2 - self.WORLD_WIDTH / 12
        top = self.WORLD_HEIGHT - self.WORLD_HEIGHT / 18 * 2
        width = self.WORLD_WIDTH / 12 * 2
        height = self.WORLD_HEIGHT / 18 * .75
        pygame.draw.rect(self.worldsurf, color, (left, top, width, height), self.kp_space)

        top = top - height * 1.5
        left = left + width + height / 2
        width = height
        pygame.draw.rect(self.worldsurf, color, (left, top, width, height), self.kp_iff)

        left = left + width + height / 2
        pygame.draw.rect(self.worldsurf, color, (left, top, width, height), self.kp_shots)

        left = left + width + height / 2
        pygame.draw.rect(self.worldsurf, color, (left, top, width, height), self.kp_points)

        left = self.WORLD_WIDTH / 2 - self.WORLD_WIDTH / 12 - width - height / 2
        pygame.draw.rect(self.worldsurf, color, (left, top, width, height), self.kp_right)

        left = left - width - height / 2
        top = top - height * 1.5
        pygame.draw.rect(self.worldsurf, color, (left, top, width, height), self.kp_thrust)

        left = left - width - height / 2
        top = top + height * 1.5
        pygame.draw.rect(self.worldsurf, color, (left, top, width, height), self.kp_left)

    def draw_complete(self):
        fpssurf = self.f96.render("Session Complete", True, (255, 0, 0))
        fpsrect = fpssurf.get_rect()
        fpsrect.centerx = self.SCREEN_WIDTH / 2
        fpsrect.centery = self.SCREEN_HEIGHT / 2
        self.screen.blit(fpssurf, fpsrect)

    def quit(self, lc):
        self.gameevents.add("game", "quit", self.ret, type='EVENT_USER')
        if self.ret == 0:
            self.gameevents.add("session", "complete", type='EVENT_SYSTEM')
        else:
            self.gameevents.add("session", "incomplete", type='EVENT_SYSTEM')
        self.process_events()
        if self.config['Logging']['logging']:
            self.log.close()
            if self.ret == 0:
                os.rename(self.log_filename, self.log_filename[:-11])
        pygame.quit()
        self.reactor.stop()

    def draw_scores(self, time=0):
        self.gameevents.add("game", "end", type='EVENT_SYSTEM')
        self.gameevents.add("scores", "show", type='EVENT_SYSTEM')
        if self.config['General']['next_gen']:
            self.draw_ng_score(time)
        elif self.config['Score']['new_scoring']:
            self.draw_new_score()
        else:
            self.draw_old_score()
        self.gameevents.add("scores", "hide", type='EVENT_SYSTEM')

    def refresh(self):
        if self.state != self.STATE_CALIBRATE:
            self.process_input()
            self.process_events()
            self.process_game_logic()
            self.draw()
            if self.config['Logging']['logging'] and self.config['Logging']['logDriver'] == 'Default':
                self.log_world()

    def start(self):
        self.lc = LoopingCall(self.refresh)
        cleanupD = self.lc.start(1.0 / self.fps)
        cleanupD.addCallbacks(self.quit)
        
    def run(self):
        reactor.callLater(0, self.start)
        reactor.run()
