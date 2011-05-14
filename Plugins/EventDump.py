"""
This is an example plugin which can listen for 
events and register new config options.
"""

class SF5Plugin(object):
    
    cfg = None
    
    def registerConfig(self, cfg):
        self.cfg = cfg
        cfg.add_setting('Logging', 'print_events', False, alias='Print Events', type=2, about='Print events to stdout')
    
    def eventCallback(self, *args, **kwargs):
        if self.cfg.get_setting('Logging','print_events'):
            print args