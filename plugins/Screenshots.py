"""
Screenshot support
"""

try:

    import os
    from jsonConfig import *
    from pycogworks import getDateTimeStamp
    import pygame
    
    PYGAME_KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
               'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p',
               'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l',
               'z', 'x', 'c', 'v', 'b', 'n', 'm', 'SPACE',
               'BACKSPACE', 'TAB', 'RETURN', 'COMMA', 'MINUS', 'PERIOD',
               'SLASH', 'SEMICOLON', 'QUOTE', 'LEFTBRACKET', 'RIGHTBRACKET',
               'BACKSLASH', 'EQUALS', 'BACKQUOTE', 'UP', 'DOWN', 'RIGHT', 'LEFT',
               'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']
    
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
                    self.app.config.add_setting('Screenshots', 'screenshot_dir', 'screenshots', alias='Screenshot Folder', type=3)
                    self.app.config.add_setting('Screenshots', 'screenshot_format', 'JPEG', alias='Screenshot Format', type=1, options=['PNG'])
                    self.app.config.add_setting('Keybindings', 'screenshot_key', 'SLASH', alias='Screenshot', type=1, options=PYGAME_KEYS)
            
            if args[3] == 'press' and args[5] == 'user' and args[4] == self.screenshot_key:
                filename = os.path.join(self.app.config['Screenshots']['screenshot_dir'], "%s.jpg" % getDateTimeStamp())
                pygame.image.save(self.app.screen, filename)

except ImportError as e:
    sys.stderr.write("Failed to load 'Screenshot' plugin, missing dependencies. [%s]\n" % e)
