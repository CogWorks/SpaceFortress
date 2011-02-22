#sounds.py
#Space Fortress 5
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2010
import pygame

class SFSound(pygame.mixer.Sound):
    def __init__(self, app, file):
        self.app = app
        if self.app.config["sound"]:
            super(SFSound, self).__init__(file)
    def __play__(self):
        if self.app.config["sound"]: super.__play__()

class Sounds(object):
    """collection of game sounds"""
    def __init__(self, app):
        super(Sounds, self).__init__()
        if app.config["sound"]: pygame.mixer.init()
        self.shell_fired = SFSound(app, "sounds/ShellFired.wav")
        self.missile_fired = SFSound(app, "sounds/MissileFired.wav")
        self.explosion = SFSound(app, "sounds/ExpFort.wav")
        self.collision = SFSound(app, "sounds/Collision.wav")
        self.vlner_reset = SFSound(app, "sounds/VulnerZeroed.wav")