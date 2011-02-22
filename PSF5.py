from __future__ import division
import tokens
from tokens.gameevent import *
import sys, os
import pygame
import argparse
from config import *
from pycogworld import *

def get_psf_version_string():
    return "SpaceFortress 5.0"

release_build = False

class Game(object):
    """Main game application"""
    def __init__(self, cogworld, condition):
        super(Game, self).__init__()
        self.cw = cogworld
        self.cond = condition
        if sys.platform == "darwin" and release_build:
            self.app_path = '../../../'
        else:
            self.app_path = '.'
        self.datapath = os.path.join(self.app_path, "data/")
        self.config = load_config("config.txt")
        pygame.display.init()
        pygame.font.init()
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
        self.sounds = tokens.sounds.Sounds(self)
        if self.config["fullscreen"]:
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.gametimer = tokens.timer.Timer()
        self.flighttimer = tokens.timer.Timer()
        self.worldsurf = pygame.Surface((self.WORLD_WIDTH, self.WORLD_HEIGHT))
        self.worldrect = self.worldsurf.get_rect()
        self.worldrect.centerx = self.SCREEN_WIDTH/2
        if not self.config["new_scoring_pos"]:
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
        self.bighex = tokens.hexagon.Hex(self, int(self.config["big_hex"]))
        self.smallhex = tokens.hexagon.Hex(self,int(self.config["small_hex"])) 
        if self.config["mine_exists"]:
            self.mine_exists = True
        else:
            self.mine_exists = False
        self.mine_list = tokens.mine.MineList(self)
    
    def setup_world(self):
        """initializes gameplay"""
        self.gameevents = GameEventList()
        self.missile_list = []
        self.shell_list = []
        self.ship = tokens.ship.Ship(self)
        if self.config["bonus_exists"]:
            self.bonus = tokens.bonus.Bonus(self)
            self.bonus_exists = True
        else:
            self.bonus_exists = False
        if self.config["fortress_exists"]:
            self.fortress = tokens.fortress.Fortress(self)
            self.fortress_exists = True
        else:
            self.fortress.exists = False
        self.gametimer.reset()
        self.flighttimer.reset()
        self.mine_list.timer.reset()
        self.mine_list.MOT_timer.reset()
        self.mine_list.MOT_switch_timer.reset()
        
    
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
    
    def process_game_logic(self):
        """processes game logic to produce game events"""
        self.ship.compute()
        for missile in self.missile_list:
            missile.compute()
        if self.fortress_exists == True:
            self.fortress.compute()
        for shell in self.shell_list:
            shell.compute()
        if self.config["hex_shrink"]:
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
        if self.flighttimer.elapsed() > int(self.config["update_timer"]):
            self.flighttimer.reset()
            if (self.ship.velocity.x **2 + self.ship.velocity.y **2)**0.5 < int(self.config["speed_threshold"]):
                self.gameevents.add("score+", "vlcty", int(self.config["VLCTY_increment"]))
                self.gameevents.add("score+", "flight", int(self.config["VLCTY_increment"]))
            else:
                self.gameevents.add("score-", "vlcty", int(self.config["VLCTY_increment"]))
                self.gameevents.add("score-", "flight", int(self.config["VLCTY_increment"]))
            if self.bighex.collide(self.ship):
                self.gameevents.add("score+", "cntrl", int(self.config["CNTRL_increment"]))
                self.gameevents.add("score+", "flight", int(self.config["CNTRL_increment"]))
            else:
                self.gameevents.add("score+", "cntrl", int(self.config["CNTRL_increment"])/2)
                self.gameevents.add("score+", "flight", int(self.config["CNTRL_increment"])/2)
        if self.bonus_exists:
            if self.bonus.visible == False and self.bonus.timer.elapsed() > int(self.config["symbol_down_time"]):
                self.gameevents.add("activate", "bonus")
            elif self.bonus.visible == True and self.bonus.timer.elapsed() >= int(self.config["symbol_up_time"]):
                self.gameevents.add("deactivate", "bonus", self.bonus.current_symbol)
    
    def process_events(self):
        """processes internal list of game events for this frame"""
        while len(self.gameevents) > 0:
            currentevent = self.gameevents.pop(0)
            command = currentevent.command
            obj = currentevent.obj
            target = currentevent.target
            if self.config["print_events"]:
                print "time %d, command %s, object %s, target %s"%(pygame.time.get_ticks(), command, obj, target)
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
                        if (self.mine_list.iff_timer.elapsed() > int(self.config["intrvl_min"])) and (self.mine_list.iff_timer.elapsed() < int(self.config["intrvl_max"])):
                            self.gameevents.add("second_tag", "foe")
                        else:
                            self.gameevents.add("second_tag", "out_of_bounds")
                elif obj == "shots":
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
                            self.gameevents.add("score++", "shots", int(self.config["bonus_missiles"]))
                            self.bonus.flag = True
                elif obj == "pnts":
                    #if current symbol is bonus but previous wasn't, set flag to deny bonus if next symbol happens to be the bonus symbol
                    if (self.bonus.current_symbol == self.bonus.bonus_symbol) and (self.bonus.prior_symbol != self.bonus.bonus_symbol):
                        self.bonus.flag = True
                        self.gameevents.add("flagged_for_first_bonus")
                    if (self.bonus.current_symbol == self.bonus.bonus_symbol) and (self.bonus.prior_symbol == self.bonus.bonus_symbol):
                        #bonus available, check flag to award or deny bonus
                        if self.bonus.flag:
                            self.gameevents.add("attempt_to_capture_flagged_bonus")
                        else:
                            self.gameevents.add("shots_pnts_capture")
                            self.gameevents.add("score++", "bonus", int(self.config["bonus_missiles"]))
                            self.gameevents.add("score++", "pnts", int(self.config["bonus_missiles"]))
                            self.bonus.flag = True
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
                if obj == "left" or obj == "right":
                    self.ship.turn_flag = False
                elif obj == "thrust":
                    self.ship.thrust_flag = False
            elif command == "warp":
                self.gameevents.add("score-", "pnts", int(self.config["warp_penalty"]))
                self.gameevents.add("score-", "flight", int(self.config["warp_penalty"])) 
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
                self.mine_list.timer.reset()
                if len(self.mine_list) > 0:
                    del self.mine_list[0]
                self.score.iff = ''
                self.score.intrvl = 0
                self.gameevents.add("score-", "mines", int(self.config["mine_timeout_penalty"]))
            elif command == "score+":
                self.score.__setattr__(obj, self.score.__getattribute__(obj) + target)
            elif command == "score-":
                self.score.__setattr__(obj, self.score.__getattribute__(obj) - target)
            elif command == "collide":
                self.process_collision(obj, target)
                    
    
    def process_collision(self, obj, target):
        """process single collision event"""
        if obj == "small_hex" and not self.smallhex.small_hex_flag:
            self.ship.velocity.x = -self.ship.velocity.x
            self.ship.velocity.y = -self.ship.velocity.y
            self.gameevents.add("score-", "pnts", int(self.config["small_hex_penalty"]))
            self.gameevents.add("score-", "flight", int(self.config["small_hex_penalty"]))
            self.smallhex.small_hex_flag = True
        elif obj == "shell":
            #remove shell, target is index of shell in shell_list
            del self.shell_list[target]
            self.gameevents.add("score-", "pnts", int(self.config["shell_hit_penalty"]))
            self.gameevents.add("score-", "fortress", int(self.config["shell_hit_penalty"]))
            self.ship.take_damage()
            if not self.ship.alive:
                self.gameevents.add("destroyed", "ship", "shell")
                self.gameevents.add("score-", "pnts", int(self.config["ship_death_penalty"]))
                self.gameevents.add("score-", "fortress", int(self.config["ship_death_penalty"]))
        elif obj.startswith("missile_"):
            #if missile hits fortress, need to check if it takes damage when mine is onscreen
            if target == "fortress" and (len(self.mine_list) == 0 or self.config["hit_fortress_while_mine"]):
                if self.ship.shot_timer.elapsed() >= int(self.config["vlner_time"]):
                    self.gameevents.add("score+", "vlner", 1)
                if self.ship.shot_timer.elapsed() < int(self.config["vlner_time"]) and self.score.vlner >= int(self.config["vlner_threshold"]):
                    self.gameevents.add("destroyed", "fortress")
                    self.fortress.alive = False
                    self.fortress.reset_timer.reset()
                    self.sounds.explosion.play()
                    self.gameevents.add("score+", "pnts", int(self.config["destroy_fortress"]))
                    self.gameevents.add("score+", "fortress", int(self.config["destroy_fortress"]))
                    self.score.vlner = 0
                    #do we reset the mine timer?
                    if self.config["fortress_resets_mine"]:
                        self.mine_list.timer.reset()
                        self.mine_list.flag = False
                if self.ship.shot_timer.elapsed() < int(self.config["vlner_time"]) and self.score.vlner < int(self.config["vlner_threshold"]):
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
            self.mine_list.timer.reset()
            self.gameevents.add("score-", "pnts", int(self.config["mine_hit_penalty"]))
            self.gameevents.add("score-", "mines", int(self.config["mine_hit_penalty"]))
            self.ship.take_damage()
            if not self.ship.alive:
                self.gameevents.add("destroyed", "ship", "shell")
                self.gameevents.add("score-", "pnts", int(self.config["ship_death_penalty"]))
                self.gameevents.add("score-", "mines", int(self.config["ship_death_penalty"]))
        elif obj == "friend_mine":
            #get rid of mine
            self.mine_list.flag = False
            self.mine_list.timer.reset()
            self.gameevents.add("score+", "mines", int(self.config["energize_friend"]))
            #amazingly, missile can hit the mine in the same frame as the mine hits the ship
            if len(self.mine_list) > 0:
                del self.mine_list[0]
            self.score.iff = ''
            self.score.intrvl = 0
        elif obj == "tagged_foe_mine":
            #get rid of mine
            self.mine_list.flag = False
            self.mine_list.timer.reset()
            self.gameevents.add("score+", "mines", int(self.config["destroy_foe"]))
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
            if len(self.mine_list) == 0:
                if missile.collide(self.fortress):
                    self.gameevents.add("collide", "missile_"+str(i), "fortress")
                    del self.missile_list[i]
            else:
                for j, mine in enumerate(self.mine_list):
                    if missile.collide(mine) and missile.collide(self.fortress):
                        self.gameevents.add("collide", "missile_"+str(i), "fortress")
                        self.gameevents.add("collide", "missile_"+str(i), "mine_"+str(j))
                        del self.missile_list[i]
                    if missile.collide(mine) and not missile.collide(self.fortress):
                        self.gameevents.add("collide", "missile_"+str(i), "mine_"+str(j))
                        del self.missile_list[i]
                    if missile.collide(self.fortress) and not missile.collide(mine):
                        self.gameevents.add("collide", "missile_"+str(i), "fortress")
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
        self.mine_list.draw()
        if self.bonus_exists:
            if self.bonus.visible:
                self.bonus.draw(self.worldsurf)
        self.screen.blit(self.scoresurf, self.scorerect)
        self.screen.blit(self.worldsurf, self.worldrect)
        pygame.display.flip()
    
    def display_foe_mines(self):
        """before game begins, present the list of IFF letters to target"""
        if self.config["print_events"]:
            print int(self.config["num_foes"]), self.mine_list.foe_letters
        self.screen.fill((0,0,0))
        top = self.f24.render("The Type-2 mines for this session are:", True, (255,255,0))
        top_rect = top.get_rect()
        top_rect.centerx = self.SCREEN_WIDTH/2
        top_rect.centery = 270
        middle = self.f96.render(", ".join(self.mine_list.foe_letters), True, (255,255,255))
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
        #self.log.write("# %f %d Foe mines: %s\n"%(time.time(), pygame.time.get_ticks(), " ".join(self.mine.foe_letters)))
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    return
    

def main(cogworld, condition):
    
    g = Game(cogworld, condition)
    if g.mine_exists:
        g.display_foe_mines()
    g.setup_world()
    while True:
        g.clock.tick(30)
        g.process_input()
        g.process_game_logic()
        g.process_events()              
        g.draw()
        if g.ship.alive == False:
            g.reset_position()

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--version', action='version', version=get_psf_version_string())
    parser.add_argument('--generate-config', action="store_true", dest="genconfig", help='Generate a full default config file.', default=argparse.SUPPRESS)
    parser.add_argument('--condition', action="store", dest="condition", help='Task Condition', metavar='COND')
    parser.add_argument('--port', action="store", dest="port", help='CogWorld RPC port')
    args = parser.parse_args()

    cogworld = None
    
    try:
        if args.genconfig:
            if gen_config("config.txt.new"):
                print 'The new config file "config.txt.new" needs to be renamed before it can be used.'
            else:
                print 'Error creating config file.'
            sys.exit(0)
        elif args.port:
            cogworld = CogWorld('localhost', args.port, 'SpaceFortress')
            ret = cogworld.connect()
            if (ret!=None):
                print 'Failed connecting to CogWorld: %s' % (ret)
                sys.exit()
    except AttributeError:
        pass
            
    main(cogworld, args.condition)
        

