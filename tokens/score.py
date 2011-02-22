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
        if not self.both and self.old != instance.old_positions:
            return 0
        return instance.positions[instance.position_map[self.name]]

    def __set__(self, instance, value):
        if self.both or self.old == instance.old_positions:
            instance.positions[instance.position_map[self.name]] = value

class Score(object):
    """collection of game scores"""
    def __init__(self, config):
        self.config = config
        #if we're using the new scoring system, PNTS == Flight, CNTRL == Fortress, VLCTY == Mines, SPEED == Bonus
        #indexed array of what score goes in which position. Setting it to 9 to use indicies 1-8
        self.position_map = {}
        for key in ('VLNER_pos', 'IFF_pos', 'INTRVL_pos', 'SHOTS_pos',
                    'PNTS_pos','CNTRL_pos', 'VLCTY_pos', 'SPEED_pos'):
            self.position_map[key] = int(self.config[key])
        num_positions = max(self.position_map.values()) + 1
        self.positions = [0] * num_positions
        self.old_positions = not self.config['new_scoring_pos']
        if self.old_positions:
            self.f = pygame.font.Font("fonts/freesansbold.ttf", 14)
        else:
            self.f = pygame.font.Font("fonts/freesansbold.ttf", 28)
        self.iff = ''
        self.shots = 100
    
    vlner = ScoreAttr('VLNER_pos', both=True)
    iff = ScoreAttr('IFF_pos', both=True)
    intrvl = ScoreAttr('INTRVL_pos', both=True)
    shots = ScoreAttr('SHOTS_pos', both=True)
    
    # Old scoring
    pnts = ScoreAttr('PNTS_pos', old=True)
    cntrl = ScoreAttr('CNTRL_pos', old=True)
    vlcty = ScoreAttr('VLCTY_pos', old=True)
    speed = ScoreAttr('SPEED_pos', old=True)
    
    # New scoring
    flight = ScoreAttr('PNTS_pos')
    fortress = ScoreAttr('CNTRL_pos')
    mines = ScoreAttr('VLCTY_pos')
    bonus = ScoreAttr('SPEED_pos')

    
        
    def draw(self, scoresurf):
        """draws all score values to screen"""      
        self.p1_surf = self.f.render("%d"%self.positions[1],0, (255,255,0))
        self.p1_rect = self.p1_surf.get_rect()
        self.p1_rect.centery = 48
        self.p1_rect.centerx = 45
        self.p2_surf = self.f.render("%d"%self.positions[2],0, (255,255,0))
        self.p2_rect = self.p2_surf.get_rect()
        self.p2_rect.centery = 48
        self.p2_rect.centerx = 134
        self.p3_surf = self.f.render("%d"%self.positions[3],0, (255,255,0))
        self.p3_rect = self.p3_surf.get_rect()
        self.p3_rect.centery = 48
        self.p3_rect.centerx = 223
        self.p4_surf = self.f.render("%d"%self.positions[4],0, (255,255,0))
        self.p4_rect = self.p4_surf.get_rect()
        self.p4_rect.centery = 48
        self.p4_rect.centerx = 312
        self.p5_surf = self.f.render("%s"%self.positions[5],0, (255,255,0))
        self.p5_rect = self.p5_surf.get_rect()
        self.p5_rect.centery = 48
        self.p5_rect.centerx = 401
        self.p6_surf = self.f.render("%d"%self.positions[6],0, (255,255,0))
        self.p6_rect = self.p6_surf.get_rect()
        self.p6_rect.centery = 48
        self.p6_rect.centerx = 490
        self.p7_surf = self.f.render("%d"%self.positions[7],0, (255,255,0))
        self.p7_rect = self.p7_surf.get_rect()
        self.p7_rect.centery = 48
        self.p7_rect.centerx = 579
        self.p8_surf = self.f.render("%d"%self.positions[8],0, (255,255,0))
        self.p8_rect = self.p8_surf.get_rect()
        self.p8_rect.centery = 48
        self.p8_rect.centerx = 668
        if self.config["new_scoring_pos"]:
            self.p1_rect.centery = 40
            self.p1_rect.centerx = 320
            self.p2_rect.centery = 40
            self.p2_rect.centerx = 660
            self.p3_rect.centery = 113
            self.p3_rect.centerx = 940
            self.p4_rect.centery = 445
            self.p4_rect.centerx = 940
            self.p5_rect.centery = 745
            self.p5_rect.centerx = 660
            self.p6_rect.centery = 745
            self.p6_rect.centerx = 320
            self.p7_rect.centery = 445
            self.p7_rect.centerx = 80
            self.p8_rect.centery = 113
            self.p8_rect.centerx = 80
        if not(int(self.config["INTRVL_pos"]) == 1 and self.intrvl == 0):
            scoresurf.blit(self.p1_surf, self.p1_rect)
        if not(int(self.config["INTRVL_pos"]) == 2 and self.intrvl == 0):
            scoresurf.blit(self.p2_surf, self.p2_rect)
        if not(int(self.config["INTRVL_pos"]) == 3 and self.intrvl == 0):
            scoresurf.blit(self.p3_surf, self.p3_rect)
        if not(int(self.config["INTRVL_pos"]) == 4 and self.intrvl == 0):
            scoresurf.blit(self.p4_surf, self.p4_rect)
        if not(int(self.config["INTRVL_pos"]) == 5 and self.intrvl == 0):
            scoresurf.blit(self.p5_surf, self.p5_rect)
        if not(int(self.config["INTRVL_pos"]) == 6 and self.intrvl == 0):
            scoresurf.blit(self.p6_surf, self.p6_rect)
        if not(int(self.config["INTRVL_pos"]) == 7 and self.intrvl == 0):
            scoresurf.blit(self.p7_surf, self.p7_rect)
        if not(int(self.config["INTRVL_pos"]) == 8 and self.intrvl == 0):
            scoresurf.blit(self.p8_surf, self.p8_rect)