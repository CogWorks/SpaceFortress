#KNOWN BUG - scores "line up" properly with either new scoring + new positions OR old scoring + old positions, but not intermixed
#score.py
#Space Fortress 5
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2010
import pygame

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
                    'PNTS_pos','CNTRL_pos', 'VLCTY_pos', 'SPEED_pos'):
            self.position_map[key] = self.app.config.get_setting('Score',key)
        num_positions = max(self.position_map.values()) + 1
        self.positions = [0] * num_positions
        self.old_positions = not self.app.config.get_setting('Score','new_scoring_pos')
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
        self.shots = self.app.config.get_setting('Missile','missile_num')
        
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
        self.NEW_SCORE_X_R_RIGHT = half_width + 428*self.app.aspect_ratio
        self.NEW_SCORE_X_L_LEFT = half_width - 432 * self.app.aspect_ratio
    
        
    def update_score(self):
        """updates positions list to reflect current scores"""
        self.positions[self.position_map["SHOTS_pos"]] = self.shots
        self.positions[self.position_map["VLNER_pos"]] = self.vlner
        self.positions[self.position_map["IFF_pos"]] = self.iff
        self.positions[self.position_map["INTRVL_pos"]] = self.intrvl
        if self.app.config.get_setting('Score','new_scoring'):
            #use Flight, Fortress, Mines, Bonus
            self.positions[self.position_map["PNTS_pos"]] = self.flight
            self.positions[self.position_map["VLCTY_pos"]] = self.mines
            self.positions[self.position_map["CNTRL_pos"]] = self.fortress
            self.positions[self.position_map["SPEED_pos"]] = self.bonus
        else:
            #use PNTS, VLCTY, CNTRL, SPEED
            self.positions[self.position_map["PNTS_pos"]] = self.pnts
            self.positions[self.position_map["VLCTY_pos"]] = self.vlcty
            self.positions[self.position_map["CNTRL_pos"]] = self.cntrl
            self.positions[self.position_map["SPEED_pos"]] = self.speed
        for item in range(1,9):
            if isinstance(self.positions[item], float):
                self.positions[item] = int(self.positions[item])
        
    def draw(self, scoresurf):
        """draws all score values to screen"""     
        #get some floats from adding fractions. Change to int for font rendering
        self.update_score()
        print self.positions
        self.p1_surf = self.f.render("%s"%str(self.positions[1]),0, (255,255,0))
        self.p1_rect = self.p1_surf.get_rect()
        self.p1_rect.centery = self.OLD_SCORE_Y_BASE
        self.p1_rect.centerx = self.OLD_SCORE_X_P1 
        self.p2_surf = self.f.render("%s"%str(self.positions[2]),0, (255,255,0))
        self.p2_rect = self.p2_surf.get_rect()
        self.p2_rect.centery = self.OLD_SCORE_Y_BASE
        self.p2_rect.centerx = self.OLD_SCORE_X_P2
        self.p3_surf = self.f.render("%s"%str(self.positions[3]),0, (255,255,0))
        self.p3_rect = self.p3_surf.get_rect()
        self.p3_rect.centery = self.OLD_SCORE_Y_BASE
        self.p3_rect.centerx = self.OLD_SCORE_X_P3
        self.p4_surf = self.f.render("%s"%str(self.positions[4]),0, (255,255,0))
        self.p4_rect = self.p4_surf.get_rect()
        self.p4_rect.centery = self.OLD_SCORE_Y_BASE
        self.p4_rect.centerx = self.OLD_SCORE_X_P4
        self.p5_surf = self.f.render("%s"%str(self.positions[5]),0, (255,255,0))
        self.p5_rect = self.p5_surf.get_rect()
        self.p5_rect.centery = self.OLD_SCORE_Y_BASE
        self.p5_rect.centerx = self.OLD_SCORE_X_P5
        self.p6_surf = self.f.render("%s"%str(self.positions[6]),0, (255,255,0))
        self.p6_rect = self.p6_surf.get_rect()
        self.p6_rect.centery = self.OLD_SCORE_Y_BASE
        self.p6_rect.centerx = self.OLD_SCORE_X_P6
        self.p7_surf = self.f.render("%s"%str(self.positions[7]),0, (255,255,0))
        self.p7_rect = self.p7_surf.get_rect()
        self.p7_rect.centery = self.OLD_SCORE_Y_BASE
        self.p7_rect.centerx = self.OLD_SCORE_X_P7
        self.p8_surf = self.f.render("%s"%str(self.positions[8]),0, (255,255,0))
        self.p8_rect = self.p8_surf.get_rect()
        self.p8_rect.centery = self.OLD_SCORE_Y_BASE
        self.p8_rect.centerx = self.OLD_SCORE_X_P8
        if self.app.config.get_setting('Score','new_scoring_pos'):
            # Bottom Left
            self.p1_rect.centery = self.NEW_SCORE_Y_C_BOTTOM
            self.p1_rect.centerx =  self.NEW_SCORE_X_C_LEFT #320
            # Bottom Right
            self.p2_rect.centery = self.NEW_SCORE_Y_C_BOTTOM
            self.p2_rect.centerx = self.NEW_SCORE_X_C_RIGHT #660
            # Right Top
            self.p3_rect.centery = self.NEW_SCORE_Y_LR_TOP
            self.p3_rect.centerx = self.NEW_SCORE_X_R_RIGHT #940
            # Right Bottom
            self.p4_rect.centery = self.NEW_SCORE_Y_LR_BOTTOM
            self.p4_rect.centerx = self.NEW_SCORE_X_R_RIGHT #940
            # Top Right
            self.p5_rect.centery = self.NEW_SCORE_Y_C_TOP
            self.p5_rect.centerx = self.NEW_SCORE_X_C_RIGHT #660
            # Top Left
            self.p6_rect.centery = self.NEW_SCORE_Y_C_TOP
            self.p6_rect.centerx = self.NEW_SCORE_X_C_LEFT #320
            # Left Bottom
            self.p7_rect.centery = self.NEW_SCORE_Y_LR_BOTTOM
            self.p7_rect.centerx = self.NEW_SCORE_X_L_LEFT #80
            # Left Tom
            self.p8_rect.centery = self.NEW_SCORE_Y_LR_TOP
            self.p8_rect.centerx = self.NEW_SCORE_X_L_LEFT #80
        
        if not(self.app.config.get_setting('Score','INTRVL_pos') == 1 and self.intrvl == 0):
            scoresurf.blit(self.p1_surf, self.p1_rect)
        if not(self.app.config.get_setting('Score','INTRVL_pos') == 2 and self.intrvl == 0):
            scoresurf.blit(self.p2_surf, self.p2_rect)
        if not(self.app.config.get_setting('Score','INTRVL_pos') == 3 and self.intrvl == 0):
            scoresurf.blit(self.p3_surf, self.p3_rect)
        if not(self.app.config.get_setting('Score','INTRVL_pos') == 4 and self.intrvl == 0):
            scoresurf.blit(self.p4_surf, self.p4_rect)
        if not(self.app.config.get_setting('Score','INTRVL_pos') == 5 and self.intrvl == 0):
            scoresurf.blit(self.p5_surf, self.p5_rect)
        if not(self.app.config.get_setting('Score','INTRVL_pos') == 6 and self.intrvl == 0):
            scoresurf.blit(self.p6_surf, self.p6_rect)
        if not(self.app.config.get_setting('Score','INTRVL_pos') == 7 and self.intrvl == 0):
            scoresurf.blit(self.p7_surf, self.p7_rect)
        if not(self.app.config.get_setting('Score','INTRVL_pos') == 8 and self.intrvl == 0):
            scoresurf.blit(self.p8_surf, self.p8_rect)