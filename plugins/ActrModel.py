"""
This is an example plugin which can listen for 
events and register new config options.
"""


class SF5Plugin(object):
    
    def __init__(self, app):
        super(SF5Plugin, self).__init__()
        self.app = app
        self.print_events = False
    
    def eventCallback(self, *args, **kwargs):
        if args[3] == 'display' and args[4] == 'preflip' and self.app.state == self.app.STATE_PLAY:
            result = []
            if self.app.fortress_exists and self.app.fortress.alive:
                result.append(self.app.fortress.FortresstoChunk())
            if self.app.ship.alive:
                result.append(self.app.ship.ShiptoChunk())
            if result:
                self.app.actr.update_display(result)
    
        

        if self.print_events and kwargs['log']:
            print args
