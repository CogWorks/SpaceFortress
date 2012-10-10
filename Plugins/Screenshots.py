"""
Screenshot support
"""

try:

    import os
    from jsonConfig import *
    from pycogworks import getDateTimeStamp
    import pygame
    
    class SF5Plugin(object):
        
        def __init__(self, app):
            super(SF5Plugin, self).__init__()
            self.app = app
            
        def ready(self):
            self.screenshot_key = eval("pygame.K_%s" % self.app.config['Keybindings']['screenshot_key'])
            if not os.path.exists(self.app.config['Screenshots']['screenshot_dir']):
                os.makedirs(self.app.config['Screenshots']['screenshot_dir'])
        
        def eventCallback(self, *args, **kwargs):
            
            if args[3] == 'config' and args[4] == 'load':
                if args[5] == 'defaults':
                    self.app.config.add_setting('Screenshots', 'screenshot_dir', 'screenshots', alias='Screenshot Folder', type=CT_LINEEDIT)
                    self.app.config.add_setting('Screenshots', 'screenshot_format', 'JPEG', alias='Screenshot Format', type=CT_COMBO, options=['PNG'])
                    self.app.config.add_setting('Keybindings', 'screenshot_key', 'SLASH', alias='Screenshot', type=CT_COMBO, options=PYGAME_KEYS)
            
            if args[3] == 'press' and args[5] == 'user' and args[4] == self.screenshot_key:
                filename = os.path.join(self.app.config['Screenshots']['screenshot_dir'], "%s.jpg" % getDateTimeStamp())
                pygame.image.save(self.app.screen, filename)

except ImportError as e:
    sys.stderr.write("Failed to load 'Screenshot' plugin, missing dependencies. [%s]\n" % e)
