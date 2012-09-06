#frame.py
#Pygame Space Fortress
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2008
import pygame

class Frame(object):
    """boundaries of game world"""
    def __init__(self, app):
        super(Frame, self).__init__()
        self.app = app
        #score labels
        self.f = pygame.font.Font("fonts/freesansbold.ttf", 14)
        self.pnts_surf = self.f.render("PNTS",0, (0,255,0))
        self.pnts_rect = self.pnts_surf.get_rect()
        self.pnts_rect.centery = 16
        self.pnts_rect.centerx = 45
        self.cntrl_surf = self.f.render("CNTRL",0, (0,255,0))
        self.cntrl_rect = self.cntrl_surf.get_rect()
        self.cntrl_rect.centery = 16
        self.cntrl_rect.centerx = 134
        self.vlcty_surf = self.f.render("VLCTY",0, (0,255,0))
        self.vlcty_rect = self.vlcty_surf.get_rect()
        self.vlcty_rect.centery = 16
        self.vlcty_rect.centerx = 223
        self.vlner_surf = self.f.render("VLNER",0, (0,255,0))
        self.vlner_rect = self.vlner_surf.get_rect()
        self.vlner_rect.centery = 16
        self.vlner_rect.centerx = 312
        self.iff_surf = self.f.render("IFF",0, (0,255,0))
        self.iff_rect = self.iff_surf.get_rect()
        self.iff_rect.centery = 16
        self.iff_rect.centerx = 401
        self.intrvl_surf = self.f.render("INTRVL",0, (0,255,0))
        self.intrvl_rect = self.intrvl_surf.get_rect()
        self.intrvl_rect.centery = 16
        self.intrvl_rect.centerx = 490
        self.speed_surf = self.f.render("SPEED",0, (0,255,0))
        self.speed_rect = self.speed_surf.get_rect()
        self.speed_rect.centery = 16
        self.speed_rect.centerx = 579
        self.shots_surf = self.f.render("SHOTS",0, (0,255,0))
        self.shots_rect = self.shots_surf.get_rect()
        self.shots_rect.centery = 16
        self.shots_rect.centerx = 668
        
        
    def draw(self, worldsurf, scoresurf):
        """Draws the game boundaries and 'table' to hold the scores"""
        pygame.draw.rect(worldsurf, (0,255,0), (0,0, 710, 625), 1) #outer 'world' boundary
        pygame.draw.rect(scoresurf, (0,255,0), (0,0,710, 63), 1) #bottom box to hold scores
        pygame.draw.line(scoresurf, (0,255,0), (0,32),(709,32)) #divides bottom box horizontally into two rows
        #the following seven lines divides the bottom box vertically into 8 columns
        pygame.draw.line(scoresurf, (0,255,0), (89, 0), (89, 64))
        pygame.draw.line(scoresurf, (0,255,0), (178, 0), (178, 64))
        pygame.draw.line(scoresurf, (0,255,0), (267, 0), (267, 64))
        pygame.draw.line(scoresurf, (0,255,0), (356, 0), (356, 64))
        pygame.draw.line(scoresurf, (0,255,0), (445, 0), (445, 64))
        pygame.draw.line(scoresurf, (0,255,0), (534, 0), (534, 64))
        pygame.draw.line(scoresurf, (0,255,0), (623, 0), (623, 64))
        #score labels
        scoresurf.blit(self.pnts_surf, self.pnts_rect)
        scoresurf.blit(self.cntrl_surf, self.cntrl_rect)
        scoresurf.blit(self.vlcty_surf, self.vlcty_rect)
        scoresurf.blit(self.vlner_surf, self.vlner_rect)
        scoresurf.blit(self.iff_surf, self.iff_rect)
        scoresurf.blit(self.intrvl_surf, self.intrvl_rect)
        scoresurf.blit(self.speed_surf, self.speed_rect)
        scoresurf.blit(self.shots_surf, self.shots_rect)
        
