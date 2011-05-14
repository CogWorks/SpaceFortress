"""
LC Technologies, Inc. Eyegaze Integration
"""
import pygame

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
    
    def eventCallback(self, *args, **kwargs):
        
        if args[2] == 'config' and args[3] == 'load':
            
            if args[4] == 'defaults':
            
                self.app.config.add_setting('Eyegaze', 'enabled', False, type=2, about='Enable eye tracking')
                self.app.config.add_setting('Eyegaze', 'eg_server', '1.0.0.21', type=3, about='EGServer Address')
                self.app.config.add_setting('Eyegaze', 'calmode', 'Every Game', type=1, alias='When To Calibrate', options=['Every Game','Once'], about='Set when eye tracker is calibrated')
                self.app.config.add_setting('Eyegaze', 'drawfix', False, type=2, alias="Draw Fixation Cross", about='Draw a fixation cross on the screen')
                
            elif args[4] == 'user':
                
                if self.app.config.get_setting('Eyegaze','enabled'):
                    self.eg = EyeGaze()
                    if self.eg.connect(self.config.get_setting('Eyegaze','eg_server')) != None:
                        self.eg = None
                    self.eg.gaze_log_fn = self.app.log_basename + ('.gaze.csv')
                    self.eg.fix_log_fn = self.app.log_basename + ('.fix.csv')
                    self.eg.start_logging()
                    
        elif args[2] == 'game':
            
            if args[3] == 'ready':
                if self.eg and self.app.config.get_setting('Eyegaze','calmode') == 'Every Game':
                    self.calibrated = self.eg.calibrate(self.app.screen)
                if self.eg and self.calibrated:
                    self.eg.data_start()
                    
            elif args[3] == 'over':
                if self.eg:
                    self.eg.data_stop()
                    
            elif args[3] == 'quit':
                if self.eg:
                    self.eg.data_stop()
                    self.eg.stop_logging()
                    self.eg.disconnect()
        
        elif args[2] == 'display':
            
            if args[3] == 'setmode':
                if self.eg and self.app.config.get_setting('Eyegaze','calmode') == 'Once':
                    self.calibrated = self.eg.calibrate(self.app.screen)
            
            if args[3] == 'preflip' and args[4] == 'main':
                if self.eg and self.app.config.get_setting('Eyegaze','drawfix'):
                    self.draw_fixation_cross(self.app.screen)