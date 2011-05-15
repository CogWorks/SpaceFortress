#gameevent.py
#this code is to be placed in the "tokens" subfolder
#Space Fortress 5
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2010

import pygame, time

class GameEvent(object):
    """an event that happens during gameplay"""
    def __init__(self, time, ticks, command, obj=None, target=None, log=True):
        super(GameEvent, self).__init__()
        self.time = time
        self.ticks = ticks
        self.command = command
        self.obj = obj
        self.target = target
        self.log = log
                
class GameEventList(list):
    """a list that holds the game events"""
    def __init__(self):
        super(GameEventList, self).__init__()
        self.callbacks = []
        
    def addCallback(self, callback):
        self.callbacks.append(callback)
        
    def deleteCallback(self, callback):
        self.callbacks.remove(callback)
        
    def deleteCallbacks(self):
        self.observers[:] = []
    
    def notify(self, *args, **kwargs):
        for callback in self.callbacks:
            callback(*args, **kwargs)
        
    def add(self, command, target=None, obj=None, log=True):
        """adds an event to the list"""
        etime = time.time()
        eticks = pygame.time.get_ticks()
        self.append(GameEvent(etime, eticks, command, target, obj, log))
        self.notify(etime, eticks, command, target, obj, log=log)