#gameevent.py
#this code is to be placed in the "tokens" subfolder
#Space Fortress 5
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2010

class GameEvent(object):
    """an event that happens during gameplay"""
    def __init__(self, command, obj=None, target=None):
        super(GameEvent, self).__init__()
        self.command = command
        self.obj = obj
        self.target = target
                
class GameEventList(list):
    """a list that holds the game events"""
    def __init__(self):
        super(GameEventList, self).__init__()
        self.observers = []
        
    def addObserver(self, observer):
        self.observers.append(observer)
        
    def deleteObserver(self, observer):
        self.observers.remove(observer)
        
    def deleteObservers(self):
        self.observers[:] = []
    
    def notifyObservers(self, *args, **kwargs):
        for observer in self.observers:
            observer.notify(*args, **kwargs)
        
    def add(self, command, target=None, obj=None):
        """adds an event to the list"""
        self.append(GameEvent(command, target, obj))
        self.notifyObservers(time.time(), pygame.time.get_ticks(), command, target, obj)