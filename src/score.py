#KNOWN BUG - scores "line up" properly with either new scoring + new positions OR old scoring + old positions, but not intermixed
#score.py
#Space Fortress 5
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2010
import pygame

import pygl2d

class ScoreAttr(object):
    def __init__(self, name, old=False, both=False):
        self.name = name
        self.old = old
        self.both = both

    def __get__(self, instance, owner):
        if instance is None:
            return self
        # if not self.both and self.old != instance.old_positions:
        #     return 0
        return instance.positions[instance.position_map[self.name]]

    def __set__(self, instance, value):
        # if self.both or self.old == instance.old_positions:
        instance.positions[instance.position_map[self.name]] = value

class Score(object):
    """collection of game scores"""

    # vlner = ScoreAttr('VLNER_pos', both=True)
    # iff = ScoreAttr('IFF_pos', both=True)
    # intrvl = ScoreAttr('INTRVL_pos', both=True)
    # shots = ScoreAttr('SHOTS_pos', both=True)
    #
    # # Old scoring
    # pnts = ScoreAttr('PNTS_pos', old=True)
    # cntrl = ScoreAttr('CNTRL_pos', old=True)
    # vlcty = ScoreAttr('VLCTY_pos', old=True)
    # speed = ScoreAttr('SPEED_pos', old=True)
    #
    # # New scoring
    # flight = ScoreAttr('PNTS_pos')
    # fortress = ScoreAttr('CNTRL_pos')
    # mines = ScoreAttr('VLCTY_pos')
    # bonus = ScoreAttr('SPEED_pos')

    def __init__(self, app):
        self.app = app
        #if we're using the new scoring system, PNTS == Flight, CNTRL == Fortress, VLCTY == Mines, SPEED == Bonus
        #indexed array of what score goes in which position. Setting it to 9 to use indicies 1-8
        self.position_map = {}
        for key in ('VLNER_pos', 'IFF_pos', 'INTRVL_pos', 'SHOTS_pos',
                    'PNTS_pos', 'CNTRL_pos', 'VLCTY_pos', 'SPEED_pos'):
            self.position_map[key] = self.app.config['Score'][key]
        num_positions = max(self.position_map.values())
        self.positions = [0] * num_positions
        self.old_positions = not self.app.config['Score']['new_scoring_pos']
        if self.old_positions:
            self.f = self.app.f
        else:
            self.f = self.app.f28
        self.vlner = 0
        self.intrvl = 0
        self.pnts = 0
        self.cntrl = 0
        self.vlcty = 0
        self.speed = 0
        self.flight = 0
        self.fortress = 0
        self.mines = 0
        self.bonus = 0
        self.iff = ''
        self.shots = self.app.config['Missile']['missile_num']

        half_width = self.app.SCREEN_WIDTH / 2

        #CONSTANTS
        self.OLD_SCORE_Y_BASE = 48 * self.app.aspect_ratio
        self.OLD_SCORE_X_P1 = 45 * self.app.aspect_ratio
        self.OLD_SCORE_X_P2 = 134 * self.app.aspect_ratio
        self.OLD_SCORE_X_P3 = 223 * self.app.aspect_ratio
        self.OLD_SCORE_X_P4 = 312 * self.app.aspect_ratio
        self.OLD_SCORE_X_P5 = 401 * self.app.aspect_ratio
        self.OLD_SCORE_X_P6 = 490 * self.app.aspect_ratio
        self.OLD_SCORE_X_P7 = 579 * self.app.aspect_ratio
        self.OLD_SCORE_X_P8 = 668 * self.app.aspect_ratio

        self.NEW_SCORE_Y_C_BOTTOM = 40 * self.app.aspect_ratio
        self.NEW_SCORE_Y_C_TOP = 745 * self.app.aspect_ratio
        self.NEW_SCORE_Y_LR_TOP = 213 * self.app.aspect_ratio
        self.NEW_SCORE_Y_LR_BOTTOM = 545 * self.app.aspect_ratio
        self.NEW_SCORE_X_C_LEFT = half_width - 192 * self.app.aspect_ratio
        self.NEW_SCORE_X_C_RIGHT = half_width + 148 * self.app.aspect_ratio
        if self.app.config['General']['next_gen']:
            self.NEW_SCORE_X_R_RIGHT = half_width + 456 * self.app.aspect_ratio
            self.NEW_SCORE_X_L_LEFT = half_width - 460 * self.app.aspect_ratio
        else:
            self.NEW_SCORE_X_R_RIGHT = half_width + 428 * self.app.aspect_ratio
            self.NEW_SCORE_X_L_LEFT = half_width - 432 * self.app.aspect_ratio

        self.scores_locations = []
        if self.app.config['Score']['new_scoring_pos']:
            self.scores_locations.append((self.NEW_SCORE_X_C_LEFT, self.NEW_SCORE_Y_C_BOTTOM))
            self.scores_locations.append((self.NEW_SCORE_X_C_RIGHT, self.NEW_SCORE_Y_C_BOTTOM))
            self.scores_locations.append((self.NEW_SCORE_X_R_RIGHT, self.NEW_SCORE_Y_LR_TOP))
            self.scores_locations.append((self.NEW_SCORE_X_R_RIGHT, self.NEW_SCORE_Y_LR_BOTTOM))
            self.scores_locations.append((self.NEW_SCORE_X_C_RIGHT, self.NEW_SCORE_Y_C_TOP))
            self.scores_locations.append((self.NEW_SCORE_X_C_LEFT, self.NEW_SCORE_Y_C_TOP))
            self.scores_locations.append((self.NEW_SCORE_X_L_LEFT, self.NEW_SCORE_Y_LR_BOTTOM))
            self.scores_locations.append((self.NEW_SCORE_X_L_LEFT, self.NEW_SCORE_Y_LR_TOP))
        else:
            self.scores_locations.append((self.OLD_SCORE_X_P1, self.OLD_SCORE_Y_BASE))
            self.scores_locations.append((self.OLD_SCORE_X_P2, self.OLD_SCORE_Y_BASE))
            self.scores_locations.append((self.OLD_SCORE_X_P3, self.OLD_SCORE_Y_BASE))
            self.scores_locations.append((self.OLD_SCORE_X_P4, self.OLD_SCORE_Y_BASE))
            self.scores_locations.append((self.OLD_SCORE_X_P5, self.OLD_SCORE_Y_BASE))
            self.scores_locations.append((self.OLD_SCORE_X_P6, self.OLD_SCORE_Y_BASE))
            self.scores_locations.append((self.OLD_SCORE_X_P7, self.OLD_SCORE_Y_BASE))
            self.scores_locations.append((self.OLD_SCORE_X_P8, self.OLD_SCORE_Y_BASE))

        self.scores_texts = [None] * num_positions
        self.scores_rects = [None] * num_positions
        self.update_score()

    def update_score(self):
        """updates positions list to reflect current scores"""
        positions = [0] * 8
        if self.app.config['General']['next_gen']:
            time = (self.app.config['General']['game_time'] - self.app.gametimer.elapsed()) / 1000.0
            if (time < 0): time = 0
            positions[1] = "%.1f" % time
            positions[0] = "%d" % self.pnts
            positions[2] = self.shots
            if self.intrvl == 0:
                positions[3] = ""
            else:
                positions[3] = "%d" % self.intrvl
            positions[6] = self.iff
            positions[7] = "%d" % self.vlner
        else:
            positions[self.position_map["SHOTS_pos"]-1] = self.shots
            positions[self.position_map["VLNER_pos"]-1] = self.vlner
            positions[self.position_map["IFF_pos"]-1] = self.iff
            positions[self.position_map["INTRVL_pos"]-1] = self.intrvl
            if self.app.config['Score']['new_scoring']:
                #use Flight, Fortress, Mines, Bonus
                positions[self.position_map["PNTS_pos"]-1] = self.flight
                positions[self.position_map["VLCTY_pos"]-1] = self.mines
                positions[self.position_map["CNTRL_pos"]-1] = self.fortress
                positions[self.position_map["SPEED_pos"]-1] = self.bonus
            else:
                #use PNTS, VLCTY, CNTRL, SPEED
                positions[self.position_map["PNTS_pos"]-1] = self.pnts
                positions[self.position_map["VLCTY_pos"]-1] = self.vlcty
                positions[self.position_map["CNTRL_pos"]-1] = self.cntrl
                positions[self.position_map["SPEED_pos"]-1] = self.speed

        for i,v in enumerate(positions):
            if positions[i] != self.positions[i]:
                self.positions[i] = positions[i] 
                self.scores_texts[i] = pygl2d.font.RenderText("%s" % str(self.positions[i]), (255, 255, 0), self.f)
                self.scores_rects[i] = self.scores_texts[i].get_rect()
                self.scores_rects[i].center = self.scores_locations[i]

    def draw(self):
        """draws all score values to screen"""
        #get some floats from adding fractions. Change to int for font rendering
        self.update_score()
        for i,v in enumerate(self.scores_texts):
            if v: v.draw(self.scores_rects[i].topleft)
        
        return
        #print self.positions
        p1_surf = pygl2d.font.RenderText("%s" % str(self.positions[1]), (255, 255, 0), self.f)
        p1_rect = p1_surf.get_rect()
        p1_rect.center = self.scores_locations[0]
        if self.app.config['General']['next_gen']:
            time = (self.app.config['General']['game_time'] - self.app.gametimer.elapsed()) / 1000.0
            if (time < 0): time = 0
            p2_surf = pygl2d.font.RenderText("%.1f" % (time), (255, 255, 0), self.f)
            p2_rect = p2_surf.get_rect()
            p2_rect.center = self.scores_locations[1]
        else:
            p2_surf = pygl2d.font.RenderText("%s" % str(self.positions[2]), (255, 255, 0), self.f)
            p2_rect = p2_surf.get_rect()
            p2_rect.center = self.scores_locations[1]
        p3_surf = pygl2d.font.RenderText("%s" % str(self.positions[3]), (255, 255, 0), self.f)
        p3_rect = p3_surf.get_rect()
        p3_rect.center = self.scores_locations[2]
        p4_surf = pygl2d.font.RenderText("%s" % str(self.positions[4]), (255, 255, 0), self.f)
        p4_rect = p4_surf.get_rect()
        p4_rect.center = self.scores_locations[3]
        p5_surf = pygl2d.font.RenderText("%s" % str(self.positions[5]), (255, 255, 0), self.f)
        p5_rect = p5_surf.get_rect()
        p5_rect.center = self.scores_locations[4]
        p6_surf = pygl2d.font.RenderText("%s" % str(self.positions[6]), (255, 255, 0), self.f)
        p6_rect = p6_surf.get_rect()
        p6_rect.center = self.scores_locations[5]
        p7_surf = pygl2d.font.RenderText("%s" % str(self.positions[7]), (255, 255, 0), self.f)
        p7_rect = p7_surf.get_rect()
        p7_rect.center = self.scores_locations[6]
        p8_surf = pygl2d.font.RenderText("%s" % str(self.positions[8]), (255, 255, 0), self.f)
        p8_rect = p8_surf.get_rect()
        p8_rect.center = self.scores_locations[7]
        if self.app.config['Score']['new_scoring_pos']:
            # Bottom Left
            p1_rect.center = self.scores_locations[0] #320
            # Bottom Right
            p2_rect.center = self.scores_locations[1] #660
            # Right Top
            p3_rect.center = self.scores_locations[2] #940
            # Right Bottom
            p4_rect.center = self.scores_locations[3] #940
            # Top Right
            p5_rect.center = self.scores_locations[4] #660
            # Top Left
            p6_rect.center = self.scores_locations[5] #320
            # Left Bottom
            p7_rect.center = self.scores_locations[6] #80
            # Left Tom
            p8_rect.center = self.scores_locations[7] #80

        if not(self.app.config['Score']['INTRVL_pos'] == 1 and self.intrvl == 0):
            p1_surf.draw(p1_rect.topleft)
        if not(self.app.config['Score']['INTRVL_pos'] == 2 and self.intrvl == 0):
            p2_surf.draw(p2_rect.topleft)
        if not(self.app.config['Score']['INTRVL_pos'] == 3 and self.intrvl == 0):
            p3_surf.draw(p3_rect.topleft)
        if not(self.app.config['Score']['INTRVL_pos'] == 4 and self.intrvl == 0):
            p4_surf.draw(p4_rect.topleft)
        if not self.app.config['General']['next_gen']:
            if not(self.app.config['Score']['INTRVL_pos'] == 5 and self.intrvl == 0):
                p5_surf.draw(p5_rect.topleft)
            if not(self.app.config['Score']['INTRVL_pos'] == 6 and self.intrvl == 0):
                p6_surf.draw(p6_rect.topleft)
        if not(self.app.config['Score']['INTRVL_pos'] == 7 and self.intrvl == 0):
            p7_surf.draw(p7_rect.topleft)
        if not(self.app.config['Score']['INTRVL_pos'] == 8 and self.intrvl == 0):
            p8_surf.draw(p8_rect.topleft)
