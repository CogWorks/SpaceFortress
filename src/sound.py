import pygame

class Sound(pygame.mixer.Sound):
    def __init__(self, app, file):
        self.app = app
        if self.app.config['General']['sound']:
            super(Sound, self).__init__(file)
    def __play__(self):
        if self.app.config['General']['sound']: super.__play__()