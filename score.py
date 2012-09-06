#score.py
#Pygame Space Fortress
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2008
import pygame

class Score(object):
    """collection of game scores"""
    def __init__(self, app):
        super(Score, self).__init__()
        self.app = app
        self.f = pygame.font.Font("fonts/freesansbold.ttf", 14)
        self.pnts = 0
        self.cntrl = 0
        self.vlcty = 0
        self.vlner = 0
        self.iff = ''
        self.intrvl = 0
        self.speed = 0
        self.shots = 100
       
        
        
    def draw(self, scoresurf):
        """draws all score values to screen"""      
        self.pnts_surf = self.f.render("%d"%self.pnts,0, (255,255,0))
        self.pnts_rect = self.pnts_surf.get_rect()
        self.pnts_rect.centery = 48
        self.pnts_rect.centerx = 45
        self.cntrl_surf = self.f.render("%d"%self.cntrl,0, (255,255,0))
        self.cntrl_rect = self.cntrl_surf.get_rect()
        self.cntrl_rect.centery = 48
        self.cntrl_rect.centerx = 134
        self.vlcty_surf = self.f.render("%d"%self.vlcty,0, (255,255,0))
        self.vlcty_rect = self.vlcty_surf.get_rect()
        self.vlcty_rect.centery = 48
        self.vlcty_rect.centerx = 223
        self.vlner_surf = self.f.render("%d"%self.vlner,0, (255,255,0))
        self.vlner_rect = self.vlner_surf.get_rect()
        self.vlner_rect.centery = 48
        self.vlner_rect.centerx = 312
        self.iff_surf = self.f.render("%s"%self.iff,0, (255,255,0))
        self.iff_rect = self.iff_surf.get_rect()
        self.iff_rect.centery = 48
        self.iff_rect.centerx = 401
        self.intrvl_surf = self.f.render("%d"%self.intrvl,0, (255,255,0))
        self.intrvl_rect = self.intrvl_surf.get_rect()
        self.intrvl_rect.centery = 48
        self.intrvl_rect.centerx = 490
        self.speed_surf = self.f.render("%d"%self.speed,0, (255,255,0))
        self.speed_rect = self.speed_surf.get_rect()
        self.speed_rect.centery = 48
        self.speed_rect.centerx = 579
        self.shots_surf = self.f.render("%d"%self.shots,0, (255,255,0))
        self.shots_rect = self.shots_surf.get_rect()
        self.shots_rect.centery = 48
        self.shots_rect.centerx = 668
        
        scoresurf.blit(self.pnts_surf, self.pnts_rect)
        scoresurf.blit(self.cntrl_surf, self.cntrl_rect)
        scoresurf.blit(self.vlcty_surf, self.vlcty_rect)
        scoresurf.blit(self.vlner_surf, self.vlner_rect)
        scoresurf.blit(self.iff_surf, self.iff_rect)
        if self.intrvl != 0:
            scoresurf.blit(self.intrvl_surf, self.intrvl_rect)
        scoresurf.blit(self.speed_surf, self.speed_rect)
        scoresurf.blit(self.shots_surf, self.shots_rect)