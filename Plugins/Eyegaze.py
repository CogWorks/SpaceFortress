"""
LC Technologies, Inc. Eyegaze Integration
"""
import pygame
from pycogworks.eyegaze import *

class SF5Plugin(object):
    
    def __init__(self, app):
        super(SF5Plugin, self).__init__()
        self.app = app
        self.eg = None
        self.calibrated = False
        
    def draw_fixation_cross(self, surface, r=10, color=(255, 0, 0)):
        if self.eg.fix_data:
            pygame.draw.line(surface, color,
                             (self.eg.fix_data.fix_x - r, self.eg.fix_data.fix_y),
                             (self.eg.fix_data.fix_x + r, self.eg.fix_data.fix_y))
            pygame.draw.line(surface, color,
                             (self.eg.fix_data.fix_x, self.eg.fix_data.fix_y - r),
                             (self.eg.fix_data.fix_x, self.eg.fix_data.fix_y + r))
            
    def logHeader(self):
        if self.eg:
            return 'egtime\tgaze_x\tgaze_y\tfixation_number\teye_motion_state\tfix_x\tfix_y\tsamples'
        else:
            return None
            
    def logCallback(self):
        log = '\tNA\tNA\tNA\tNA\tNA\tNA\tNA\tNA'
        if self.eg and self.eg.eg_data:
            log = '\t%f\t%d\t%d' % (self.eg.eg_data['gazetime'], self.eg.eg_data['x'], self.eg.eg_data['y'])
            if self.eg.fix_data and self.eg.fix_data.eye_motion_state > 0:
                log = "%s\t%d\t%d\t%d\t%d" % (log, self.eg.fix_count + 1, self.eg.fix_data.eye_motion_state, self.eg.fix_data.fix_x, self.eg.fix_data.fix_y, self.eg.fix_data.fix_duration)
            else:
                log = '%s\t\t\t\t\t' % (log)
        return log
    
    def eventCallback(self, *args, **kwargs):
        
        if args[3] == 'config' and args[4] == 'load':
            
            if args[5] == 'defaults':
            
                self.app.config.add_setting('Eyegaze', 'enabled', False, type=2, about='Enable eye tracking')
                self.app.config.add_setting('Eyegaze', 'eg_server', '1.0.0.21', type=3, about='EGServer Address')
                self.app.config.add_setting('Eyegaze', 'calmode', 'Every Game', type=1, alias='When To Calibrate', options=['Every Game','Once'], about='Set when eye tracker is calibrated')
                self.app.config.add_setting('Eyegaze', 'drawfix', False, type=2, alias="Draw Fixation Cross", about='Draw a fixation cross on the screen')
                
        elif args[3] == 'log' and args[4] == "basename" and args[5] == 'ready':
                
            if self.app.config.get_setting('Eyegaze','enabled'):
                self.eg = EyeGaze()
                ret = self.eg.connect(self.app.config.get_setting('Eyegaze','eg_server'))
                if ret != None:
                    self.eg = None
                else:
                    self.eg.gaze_log_fn = self.app.log_basename + ('.gaze.txt')
                    self.eg.fix_log_fn = self.app.log_basename + ('.fix.txt')
                    self.eg.start_logging()
                    
        elif args[3] == 'game':
            
            if args[4] == 'ready':
                if self.eg and self.app.config.get_setting('Eyegaze','calmode') == 'Every Game':
                    self.calibrated = self.eg.calibrate(self.app.screen)
                if self.eg and self.calibrated:
                    self.eg.data_start()
                    
            elif args[4] == 'over':
                if self.eg:
                    self.eg.data_stop()
                    
            elif args[4] == 'quit':
                if self.eg:
                    self.eg.data_stop()
                    self.eg.stop_logging()
                    self.eg.disconnect()
        
        elif args[3] == 'display':
            
            if args[4] == 'setmode':
                if self.eg and self.app.config.get_setting('Eyegaze','calmode') == 'Once':
                    self.calibrated = self.eg.calibrate(self.app.screen)
            
            if args[4] == 'preflip' and args[4] == 'main':
                if self.eg and self.app.config.get_setting('Eyegaze','drawfix'):
                    self.draw_fixation_cross(self.app.screen)