#fortress.py
#this code is to be placed in the "sf_object" subfolder
#Pygame Space Fortress
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2008
from __future__ import division
from Vector2D import Vector2D
import math
import sf_object
import pygame
from timer import Timer as clock_timer
from timer_by_frame import Timer as frame_timer

class Fortress(sf_object.object.Object):
    """represents the fortress object that typically appears in the center of the worldsurf"""
    def __init__(self, app):
        super(Fortress, self).__init__()
        self.fortress_color_change = app.config["fortress-color"]
        self.app = app
        self.position.x = 355
        self.position.y = 315
        self.start_position.x = 355
        self.start_position.y = 315
        self.collision_radius = 18 #I'm making this up
        self.last_orientation = self.orientation 
        self.shell_alive = False
        self.automated = True
        self.fire_lock = 22
        self.thrust_flag = False #almost guaranteed that we won't be using this <mcd>
        self.turn_flag = False #won't use - just for manual fortress control <mcd>
        self.fire_flag = False #why am I wasting my time with these? <mcd>
        self.target = None
        self.target_str = "" #java code has two attributes called target with Hungarian notation. BAH <mcd>
        self.turn_threshold = 1
        self.double_shot_interval = 1
        self.lock_interval = 1
        self.thrust_speed = 0.0
        self.turn_speed = 0
        self.velocity_ratio = 0.0 #bullocks! The fortress doesn't move! <mcd>
        self.extra_damage_limit = 1000
        self.half_size = 30 #I can't find what this is supposed to be - it's used heavily in RSF's compute_fortess()
        self.base_line = sf_object.line.Line()
        self.center_line = sf_object.line.Line()
        self.l_wing_line = sf_object.line.Line()
        self.r_wing_line = sf_object.line.Line()
        if self.app.config["act-r"] == "t":
            Timer = frame_timer #why isn't this accessible outside?
        else:
            Timer = clock_timer
        self.timer = Timer(self.app)
        self.sector_size = 10
        self.lock_time = 1000
        
  
    def compute(self, app):
        """determines orientation of fortress"""
        if app.ship.alive:
            self.orientation = self.to_target_orientation(app.ship) // self.sector_size * self.sector_size #integer division truncates
        if self.orientation != self.last_orientation:
            self.last_orientation = self.orientation
            self.timer.reset()
        if self.timer.elapsed() >= self.lock_time and app.ship.alive and app.fortress.alive:
            app.log.write("# fortress fired\n")
            self.fire(app.ship)
            self.timer.reset()
            
    def fire(self, ship):
        self.app.sounds.shell_fired.play()
        self.app.shell_list.append(sf_object.shell.Shell(self.app, self.to_target_orientation(ship)))
        
    def draw(self, worldsurf):
        """draws fortress to worldsurf"""
        #photoshop measurement shows 36 pixels long, and two wings 18 from center and 18 long
        #these formulae rotate about the origin. Need to translate to origin, rotate, and translate back
        self.sinphi = math.sin(math.radians((self.orientation) % 360))
        self.cosphi = math.cos(math.radians((self.orientation) % 360))
        x1 = self.position.x
        y1 = self.position.y
        x2 = 36 * self.cosphi + self.position.x
        y2 = -(36 * self.sinphi) + self.position.y
        #x3, y3 = 18, -18
        x3 = 18 * self.cosphi - -18 * self.sinphi + self.position.x
        y3 = -(-18 * self.cosphi + 18 * self.sinphi) + self.position.y
        #x4, y4 = 0, -18
        x4 = -(-18 * self.sinphi) + self.position.x
        y4 = -(-18 * self.cosphi) + self.position.y
        #x5, y5 = 18, 18
        x5 = 18 * self.cosphi - 18 * self.sinphi + self.position.x
        y5 = -(18 * self.cosphi + 18 * self.sinphi) + self.position.y
        #x6, y6 = 0, 18
        x6 = - (18 * self.sinphi) + self.position.x
        y6 = -(18 * self.cosphi) + self.position.y

        if self.fortress_color_change == "t" and self.app.score.vlner >= 10:
            color = (255,0,0)
        else:
            color = (255,255,0)
        
        pygame.draw.line(worldsurf, color, (x1,y1), (x2, y2))
        pygame.draw.line(worldsurf, color, (x3,y3), (x5, y5))
        pygame.draw.line(worldsurf, color, (x3,y3), (x4, y4))
        pygame.draw.line(worldsurf, color, (x5,y5), (x6, y6))
        
       
    def draw2(self, worldsurf):
        """old function to determine lines based on orientation, and draws Fortress to worldsurf"""
        xfuse = yfuse = 0.0
        cosphi = math.cos(math.radians(self.orientation))
        sinphi = math.sin(math.radians(self.orientation))
        #compute body center?
        xfuse = self.position.x + self.half_size * 0.5 * sinphi
        yfuse = self.position.y - self.half_size * 0.5 * cosphi
        
        self.center_line.x1 = self.position.x
        self.center_line.y1 = self.position.y
        self.center_line.x2 = self.position.x + self.half_size * sinphi
        self.center_line.y2 = self.position.y - self.half_size * cosphi

        #the length of the base line is 0.8 * size of fortress, and it is at 90 degrees to the center line
        self.base_line.x1 = xfuse + 0.4 * self.half_size * cosphi
        self.base_line.y1 = yfuse + 0.4 * self.half_size * sinphi
        self.base_line.x2 = xfuse - 0.4 * self.half_size * cosphi
        self.base_line.y2 = yfuse - 0.4 * self.half_size * sinphi
        
        #from the original code, a shift of 0.5,0.5 is added for unknown reasons.
        self.base_line.shift_line(0.5, 0.5)

        self.l_wing_line.x1 = self.base_line.x1
        self.l_wing_line.y1 = self.base_line.y1
        self.l_wing_line.x2 = self.l_wing_line.x1 - self.half_size * 0.5 * sinphi
        self.l_wing_line.y2 = self.l_wing_line.y1 + self.half_size * 0.5 * cosphi

        self.r_wing_line.x1 = self.base_line.x2;
        self.r_wing_line.y1 = self.base_line.y2;
        self.r_wing_line.x2 = self.r_wing_line.x1 - self.half_size * 0.5 * sinphi
        self.r_wing_line.y2 = self.r_wing_line.y1 + self.half_size * 0.5 * cosphi
        
        pygame.draw.line(worldsurf, (255,255,0), (self.center_line.x1,self.center_line.y1), \
            (self.center_line.x2,self.center_line.y2))
        pygame.draw.line(worldsurf, (255,255,0), (self.base_line.x1,self.base_line.y1), \
            (self.base_line.x2,self.base_line.y2))
        pygame.draw.line(worldsurf, (255,255,0), (self.l_wing_line.x1,self.l_wing_line.y1), \
            (self.l_wing_line.x2,self.l_wing_line.y2))
        pygame.draw.line(worldsurf, (255,255,0), (self.r_wing_line.x1,self.r_wing_line.y1), \
            (self.r_wing_line.x2,self.r_wing_line.y2))