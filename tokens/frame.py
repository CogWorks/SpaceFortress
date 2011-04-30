#frame.py
#Space Fortress 5
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2010
import pygame, os

class Frame(object):
    """boundaries of game world"""
    def __init__(self, app):
        self.app = app
        super(Frame, self).__init__()
        self.linewidth = self.app.config.get_setting('General','linewidth')
        self.f = pygame.font.Font(self.app.fp, int(14*self.app.aspect_ratio))
        #if we're using the new scoring system, PNTS == Flight, CNTRL == Fortress, VLCTY == Mines, SPEED == Bonus
        #indexed array of what score goes in which position. Setting it to 9 to use indicies 1-8
        positions = [0]*9
        positions[self.app.config.get_setting('Score','VLNER_pos')] = "VLNER"
        positions[self.app.config.get_setting('Score','IFF_pos')] = "IFF"
        positions[self.app.config.get_setting('Score','INTRVL_pos')] = "INTRVL"
        positions[self.app.config.get_setting('Score','SHOTS_pos')] = "SHOTS"
        if not self.app.config.get_setting('Score','new_scoring'):
            positions[self.app.config.get_setting('Score','PNTS_pos')] = "PNTS"
            positions[self.app.config.get_setting('Score','CNTRL_pos')] = "CNTRL"
            positions[self.app.config.get_setting('Score','VLCTY_pos')] = "VLCTY"
            positions[self.app.config.get_setting('Score','SPEED_pos')] = "SPEED"
        else:
            positions[self.app.config.get_setting('Score','PNTS_pos')] = "FLIGHT"
            positions[self.app.config.get_setting('Score','CNTRL_pos')] = "FORTRESS"
            positions[self.app.config.get_setting('Score','VLCTY_pos')] = "MINES"
            positions[self.app.config.get_setting('Score','SPEED_pos')] = "BONUS"
        #score labels
        self.p1_surf = self.f.render(positions[1],0, (0,255,0))
        self.p1_rect = self.p1_surf.get_rect()
        self.p1_rect.centery = 16*self.app.aspect_ratio
        self.p1_rect.centerx = 45*self.app.aspect_ratio
        self.p2_surf = self.f.render(positions[2],0, (0,255,0))
        self.p2_rect = self.p2_surf.get_rect()
        self.p2_rect.centery = 16*self.app.aspect_ratio
        self.p2_rect.centerx = 134*self.app.aspect_ratio
        self.p3_surf = self.f.render(positions[3],0, (0,255,0))
        self.p3_rect = self.p3_surf.get_rect()
        self.p3_rect.centery = 16*self.app.aspect_ratio
        self.p3_rect.centerx = 223*self.app.aspect_ratio
        self.p4_surf = self.f.render(positions[4],0, (0,255,0))
        self.p4_rect = self.p4_surf.get_rect()
        self.p4_rect.centery = 16*self.app.aspect_ratio
        self.p4_rect.centerx = 312*self.app.aspect_ratio
        self.p5_surf = self.f.render(positions[5],0, (0,255,0))
        self.p5_rect = self.p5_surf.get_rect()
        self.p5_rect.centery = 16*self.app.aspect_ratio
        self.p5_rect.centerx = 401*self.app.aspect_ratio
        self.p6_surf = self.f.render(positions[6],0, (0,255,0))
        self.p6_rect = self.p6_surf.get_rect()
        self.p6_rect.centery = 16*self.app.aspect_ratio
        self.p6_rect.centerx = 490*self.app.aspect_ratio
        self.p7_surf = self.f.render(positions[7],0, (0,255,0))
        self.p7_rect = self.p7_surf.get_rect()
        self.p7_rect.centery = 16*self.app.aspect_ratio
        self.p7_rect.centerx = 579*self.app.aspect_ratio
        self.p8_surf = self.f.render(positions[8],0, (0,255,0))
        self.p8_rect = self.p8_surf.get_rect()
        self.p8_rect.centery = 16*self.app.aspect_ratio
        self.p8_rect.centerx = 668*self.app.aspect_ratio
        if self.app.config.get_setting('Score','new_scoring_pos'):
            half_width = self.app.SCREEN_WIDTH / 2
            self.p1_rect.centery = 15*self.app.aspect_ratio
            self.p1_rect.centerx = half_width - 192*self.app.aspect_ratio #320
            self.p2_rect.centery = 15*self.app.aspect_ratio
            self.p2_rect.centerx = half_width + 148*self.app.aspect_ratio #660
            self.p3_rect.centery = 188*self.app.aspect_ratio
            self.p3_rect.centerx = half_width + 428*self.app.aspect_ratio #940
            self.p4_rect.centery = 520*self.app.aspect_ratio
            self.p4_rect.centerx = half_width + 428*self.app.aspect_ratio #940
            self.p5_rect.centery = 720*self.app.aspect_ratio
            self.p5_rect.centerx = half_width + 148*self.app.aspect_ratio #660
            self.p6_rect.centery = 720*self.app.aspect_ratio
            self.p6_rect.centerx = half_width - 192*self.app.aspect_ratio #320
            self.p7_rect.centery = 520*self.app.aspect_ratio
            self.p7_rect.centerx = half_width - 432*self.app.aspect_ratio #80
            self.p8_rect.centery = 188*self.app.aspect_ratio
            self.p8_rect.centerx = half_width - 432*self.app.aspect_ratio #80
            
        
    def draw(self, worldsurf, scoresurf):
        """Draws the game boundaries and 'table' to hold the scores"""
        worldsurf.fill((0,0,0))
        scoresurf.fill((0,0,0))
        pygame.draw.rect(worldsurf, (0,255,0), (0,0, self.app.WORLD_WIDTH, self.app.WORLD_HEIGHT), self.linewidth) #outer 'world' boundary
        if not self.app.config.get_setting('Score','new_scoring_pos'): #draw frame along bottom of gameworld
            pygame.draw.rect(scoresurf, (0,255,0), (0,0,710*self.app.aspect_ratio, 63*self.app.aspect_ratio), self.linewidth) #bottom box to hold scores
            pygame.draw.line(scoresurf, (0,255,0), (0,32*self.app.aspect_ratio),(709*self.app.aspect_ratio,32*self.app.aspect_ratio), self.linewidth) #divides bottom box horizontally into two rows
            #the following seven lines divides the bottom box vertically into 8 columns
            pygame.draw.line(scoresurf, (0,255,0), (89*self.app.aspect_ratio, 0), (89*self.app.aspect_ratio, 62*self.app.aspect_ratio), self.linewidth)
            pygame.draw.line(scoresurf, (0,255,0), (178*self.app.aspect_ratio, 0), (178*self.app.aspect_ratio, 62*self.app.aspect_ratio), self.linewidth)
            pygame.draw.line(scoresurf, (0,255,0), (267*self.app.aspect_ratio, 0), (267*self.app.aspect_ratio, 62*self.app.aspect_ratio), self.linewidth)
            pygame.draw.line(scoresurf, (0,255,0), (356*self.app.aspect_ratio, 0), (356*self.app.aspect_ratio, 62*self.app.aspect_ratio), self.linewidth)
            pygame.draw.line(scoresurf, (0,255,0), (445*self.app.aspect_ratio, 0), (445*self.app.aspect_ratio, 62*self.app.aspect_ratio), self.linewidth)
            pygame.draw.line(scoresurf, (0,255,0), (534*self.app.aspect_ratio, 0), (534*self.app.aspect_ratio, 62*self.app.aspect_ratio), self.linewidth)
            pygame.draw.line(scoresurf, (0,255,0), (623*self.app.aspect_ratio, 0), (623*self.app.aspect_ratio, 62*self.app.aspect_ratio), self.linewidth)
        else: #draw frame in "eye-tracker-friendly" format
            half_width = self.app.SCREEN_WIDTH / 2
            pygame.draw.rect(scoresurf, (0,255,0), (half_width - 355*self.app.aspect_ratio, 5*self.app.aspect_ratio, 710*self.app.aspect_ratio, 57*self.app.aspect_ratio), self.linewidth)
            pygame.draw.rect(scoresurf, (0,255,0), (half_width + 366*self.app.aspect_ratio, 70*self.app.aspect_ratio, 130*self.app.aspect_ratio, 626*self.app.aspect_ratio), self.linewidth)
            pygame.draw.rect(scoresurf, (0,255,0), (half_width - 355*self.app.aspect_ratio, 705*self.app.aspect_ratio, 710*self.app.aspect_ratio, 57*self.app.aspect_ratio), self.linewidth)
            pygame.draw.rect(scoresurf, (0,255,0), (half_width - 495*self.app.aspect_ratio, 70*self.app.aspect_ratio, 130*self.app.aspect_ratio, 626*self.app.aspect_ratio), self.linewidth)
            # pygame.draw.rect(scoresurf, (0,255,0), (157, 5, 710, 57), self.linewidth)
            # pygame.draw.rect(scoresurf, (0,255,0), (878, 70, 130, 626), self.linewidth)
            # pygame.draw.rect(scoresurf, (0,255,0), (157, 705, 710, 57), self.linewidth)
            # pygame.draw.rect(scoresurf, (0,255,0), (17, 70, 130, 626), self.linewidth)
        #score labels
        scoresurf.blit(self.p1_surf, self.p1_rect)
        scoresurf.blit(self.p2_surf, self.p2_rect)
        scoresurf.blit(self.p3_surf, self.p3_rect)
        scoresurf.blit(self.p4_surf, self.p4_rect)
        scoresurf.blit(self.p5_surf, self.p5_rect)
        scoresurf.blit(self.p6_surf, self.p6_rect)
        scoresurf.blit(self.p7_surf, self.p7_rect)
        scoresurf.blit(self.p8_surf, self.p8_rect)
        
