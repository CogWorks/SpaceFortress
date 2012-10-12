#sounds.py
#Space Fortress 5
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2010
import pygame, os

class SFSound(pygame.mixer.Sound):
    def __init__(self, app, file):
        self.app = app
        if self.app.config['General']['sound']:
            super(SFSound, self).__init__(file)
    def __play__(self):
        if self.app.config['General']['sound']: super.__play__()

class Sounds(object):
    """collection of game sounds"""
    def __init__(self, app):
        super(Sounds, self).__init__()
        if app.config['General']['sound']:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(32)
        self.shell_fired = SFSound(app, os.path.join(app.approot, "sounds/ShellFired.wav"))
        self.missile_fired = SFSound(app, os.path.join(app.approot, "sounds/MissileFired.wav"))
        self.explosion = SFSound(app, os.path.join(app.approot, "sounds/ExpFort.wav"))
        self.collision = SFSound(app, os.path.join(app.approot, "sounds/Collision.wav"))
        self.vlner_reset = SFSound(app, os.path.join(app.approot, "sounds/VulnerZeroed.wav"))
        self.bonus_success = SFSound(app, os.path.join(app.approot, "sounds/bonus_success.wav"))
        self.bonus_fail = SFSound(app, os.path.join(app.approot, "sounds/bonus_fail.wav"))
        self.empty = SFSound(app, os.path.join(app.approot, "sounds/emptychamber.wav"))
