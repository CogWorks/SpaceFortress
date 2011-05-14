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
        
        if args[2] == 'config' and args[3] == 'load':
            if args[4] == 'defaults':
                self.app.config.add_setting('Logging', 'print_events', False, alias='Print Events', type=2, about='Print events to stdout')
                
            elif args[4] == 'user':
                self.print_events = self.app.config.get_setting('Logging','print_events')

        if self.print_events and kwargs['log']:
            print args