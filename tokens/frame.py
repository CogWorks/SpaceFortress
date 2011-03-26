#frame.py
#Space Fortress 5
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2010
import pygame

class Frame(object):
    """boundaries of game world"""
    def __init__(self, config):
        super(Frame, self).__init__()
        self.config = config
        self.linewidth = int(config["linewidth"])
        self.f = pygame.font.Font("fonts/freesansbold.ttf", 14)
        #if we're using the new scoring system, PNTS == Flight, CNTRL == Fortress, VLCTY == Mines, SPEED == Bonus
        #indexed array of what score goes in which position. Setting it to 9 to use indicies 1-8
        positions = [0]*9
        positions[int(config["VLNER_pos"])] = "VLNER"
        positions[int(config["IFF_pos"])] = "IFF"
        positions[int(config["INTRVL_pos"])] = "INTRVL"
        positions[int(config["SHOTS_pos"])] = "SHOTS"
        if not config["new_scoring"]:
            positions[int(config["PNTS_pos"])] = "PNTS"
            positions[int(config["CNTRL_pos"])] = "CNTRL"
            positions[int(config["VLCTY_pos"])] = "VLCTY"
            positions[int(config["SPEED_pos"])] = "SPEED"
        else:
            positions[int(config["PNTS_pos"])] = "FLIGHT"
            positions[int(config["CNTRL_pos"])] = "FORTRESS"
            positions[int(config["VLCTY_pos"])] = "MINES"
            positions[int(config["SPEED_pos"])] = "BONUS"
        #score labels
        self.p1_surf = self.f.render(positions[1],0, (0,255,0))
        self.p1_rect = self.p1_surf.get_rect()
        self.p1_rect.centery = 16
        self.p1_rect.centerx = 45
        self.p2_surf = self.f.render(positions[2],0, (0,255,0))
        self.p2_rect = self.p2_surf.get_rect()
        self.p2_rect.centery = 16
        self.p2_rect.centerx = 134
        self.p3_surf = self.f.render(positions[3],0, (0,255,0))
        self.p3_rect = self.p3_surf.get_rect()
        self.p3_rect.centery = 16
        self.p3_rect.centerx = 223
        self.p4_surf = self.f.render(positions[4],0, (0,255,0))
        self.p4_rect = self.p4_surf.get_rect()
        self.p4_rect.centery = 16
        self.p4_rect.centerx = 312
        self.p5_surf = self.f.render(positions[5],0, (0,255,0))
        self.p5_rect = self.p5_surf.get_rect()
        self.p5_rect.centery = 16
        self.p5_rect.centerx = 401
        self.p6_surf = self.f.render(positions[6],0, (0,255,0))
        self.p6_rect = self.p6_surf.get_rect()
        self.p6_rect.centery = 16
        self.p6_rect.centerx = 490
        self.p7_surf = self.f.render(positions[7],0, (0,255,0))
        self.p7_rect = self.p7_surf.get_rect()
        self.p7_rect.centery = 16
        self.p7_rect.centerx = 579
        self.p8_surf = self.f.render(positions[8],0, (0,255,0))
        self.p8_rect = self.p8_surf.get_rect()
        self.p8_rect.centery = 16
        self.p8_rect.centerx = 668
        if config["new_scoring_pos"]:
            self.p1_rect.centery = 15
            self.p1_rect.centerx = 320
            self.p2_rect.centery = 15
            self.p2_rect.centerx = 660
            self.p3_rect.centery = 188
            self.p3_rect.centerx = 940
            self.p4_rect.centery = 520
            self.p4_rect.centerx = 940
            self.p5_rect.centery = 720
            self.p5_rect.centerx = 660
            self.p6_rect.centery = 720
            self.p6_rect.centerx = 320
            self.p7_rect.centery = 520
            self.p7_rect.centerx = 80
            self.p8_rect.centery = 188
            self.p8_rect.centerx = 80
            
        
    def draw(self, worldsurf, scoresurf):
        """Draws the game boundaries and 'table' to hold the scores"""
        worldsurf.fill((0,0,0))
        scoresurf.fill((0,0,0))
        pygame.draw.rect(worldsurf, (0,255,0), (0,0, 710, 625), self.linewidth) #outer 'world' boundary
        if not self.config["new_scoring_pos"]: #draw frame along bottom of gameworld
            pygame.draw.rect(scoresurf, (0,255,0), (0,0,710, 63), self.linewidth) #bottom box to hold scores
            pygame.draw.line(scoresurf, (0,255,0), (0,32),(709,32), self.linewidth) #divides bottom box horizontally into two rows
            #the following seven lines divides the bottom box vertically into 8 columns
            pygame.draw.line(scoresurf, (0,255,0), (89, 0), (89, 64), self.linewidth)
            pygame.draw.line(scoresurf, (0,255,0), (178, 0), (178, 64), self.linewidth)
            pygame.draw.line(scoresurf, (0,255,0), (267, 0), (267, 64), self.linewidth)
            pygame.draw.line(scoresurf, (0,255,0), (356, 0), (356, 64), self.linewidth)
            pygame.draw.line(scoresurf, (0,255,0), (445, 0), (445, 64), self.linewidth)
            pygame.draw.line(scoresurf, (0,255,0), (534, 0), (534, 64), self.linewidth)
            pygame.draw.line(scoresurf, (0,255,0), (623, 0), (623, 64), self.linewidth)
        else: #draw frame in "eye-tracker-friendly" format
            pygame.draw.rect(scoresurf, (0,255,0), (157, 5, 710, 57), self.linewidth)
            pygame.draw.rect(scoresurf, (0,255,0), (878, 70, 130, 626), self.linewidth)
            pygame.draw.rect(scoresurf, (0,255,0), (157, 705, 710, 57), self.linewidth)
            pygame.draw.rect(scoresurf, (0,255,0), (17, 70, 130, 626), self.linewidth)
        #score labels
        scoresurf.blit(self.p1_surf, self.p1_rect)
        scoresurf.blit(self.p2_surf, self.p2_rect)
        scoresurf.blit(self.p3_surf, self.p3_rect)
        scoresurf.blit(self.p4_surf, self.p4_rect)
        scoresurf.blit(self.p5_surf, self.p5_rect)
        scoresurf.blit(self.p6_surf, self.p6_rect)
        scoresurf.blit(self.p7_surf, self.p7_rect)
        scoresurf.blit(self.p8_surf, self.p8_rect)
        
