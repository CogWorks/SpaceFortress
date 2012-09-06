#timer_by_frame.py
#Pygame Space Fortress
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2008
from __future__ import division
import pygame

class Timer(object):
    """timer that operates by frame count, and returns equivalent 'time'"""
    def __init__(self, app):
        super(Timer, self).__init__()
        self.app = app
        self.start_time = self.app.game_frame
        self.frame_factor = 1000/self.app.frames_per_second #number of milliseconds per frame
        
    def elapsed(self):
        """time elapsed since timer created"""
        return (self.app.game_frame - self.start_time) * self.frame_factor
        
    def reset(self):
        """resets timer to current time"""
        self.start_time = self.app.game_frame
    
