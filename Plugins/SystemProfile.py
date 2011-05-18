"""
Gets hardware info from Apple computers and writes it to log file
"""

import sys, subprocess

def getHWInfo():
    output = subprocess.Popen(["system_profiler", "SPHardwareDataType"], stdout=subprocess.PIPE).communicate()[0]
    output = map(lambda x: x.strip(), output[output.find('Overview:')+len('Overview:'):].strip().split('\n'))
    info = {}
    for val in output:
        tmp = val.split(':')
        info[tmp[0].strip()] = tmp[1].strip()
    return info

class SF5Plugin(object):
    
    def __init__(self, app):
        super(SF5Plugin, self).__init__()
        self.app = app
    
    def eventCallback(self, *args, **kwargs):
        
        if args[3] == 'config' and args[4] == 'load':
            if args[5] == 'defaults':
                if sys.platform == 'darwin':
                    self.app.config.add_setting('SystemProfile', 'log_mac_hw', False, type=2)
                
        elif args[3] == 'log':
    
            if args[4] == 'header' and args[5] == 'ready':
                
                if self.app.config.get_setting('SystemProfile','log_mac_hw'):
                    info = getHWInfo()
                    self.app.gameevents.add("exp_hw", "model", info['Model Identifier'], type='EVENT_SYSTEM')
                    self.app.gameevents.add("exp_hw", "processor", info['Processor Name'], type='EVENT_SYSTEM')
                    self.app.gameevents.add("exp_hw", "processors", info['Number Of Processors'], type='EVENT_SYSTEM')
                    self.app.gameevents.add("exp_hw", "cores", info['Total Number Of Cores'], type='EVENT_SYSTEM')
                    self.app.gameevents.add("exp_hw", "cpu_speed", info['Processor Speed'], type='EVENT_SYSTEM')
                    self.app.gameevents.add("exp_hw", "memory", info['Memory'], type='EVENT_SYSTEM')