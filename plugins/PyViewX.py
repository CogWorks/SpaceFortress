"""
PyViewX Integration
"""
try:
    import sys
    import json
    import pygame
    import numpy as np
    from pyviewx.client import iViewXClient, Dispatcher
    from pyviewx.pygame import CalibratorGL as Calibrator

    class SF5Plugin(object):
    
        name = 'PyViewX'
    
        d = Dispatcher()
    
        header = ["gazetime", "gaze_type", "left_gaze_x", "right_gaze_x", "left_gaze_y", "right_gaze_y",
                  "left_pupil_x", "right_pupil_x", "left_pupil_y", "right_pupil_y",
                  "left_eye_x", "right_eye_x", "left_eye_y", "right_eye_y", "left_eye_z", "right_eye_z"]
    
        logDrivers = [ 'Samples' ]
    
        def __init__(self, app):
            super(SF5Plugin, self).__init__()
            self.app = app
            self.client = None
            self.post_calibrate_mode = -1
            self.eye_data = None
            self.null_data = ["NA"] * len(self.header)
    
        def ready(self):
            if self.app.config[self.name]['enabled']:
                self.client = iViewXClient(self.app.config[self.name]['server_address'], int(self.app.config['PyViewX']['server_outport']))
                self.client.addDispatcher(self.d)
                if self.client:
                    if self.app.config[self.name]['calmode'] == 'Once':
                        self.post_calibrate_mode = self.app.state
                        self.app.state = self.app.STATE_CALIBRATE
                    self.app.reactor.listenUDP(int(self.app.config[self.name]['server_inport']), self.client)
                    self.startDataStreaming()
    
        def logHeader(self):
            if self.client:
                return self.header
            else:
                return []
    
        def logCallback(self):
            if self.eye_data:
                return self.eye_data
            else:
                return self.null_data
    
        @d.listen('ET_SPL')
        def iViewXEvent(self, inResponse):
            self.eye_data = inResponse
            if self.app.config['Logging']['logging'] and self.app.config['Logging']['logDriver'] == 'PyViewX:Samples':
                self.app.log_world()
    
        def startDataStreaming(self):
            self.client.setDataFormat('%TS %ET %SX %SY %DX %DY %EX %EY %EZ')
            self.client.startDataStreaming()
    
        def stopDataStreaming(self):
            self.client.stopDataStreaming()
    
        def calibrationDone(self, lc, results):
            self.app.gameevents.add("calibration", "results", "'%s'" % json.dumps(results, encoding="cp1252"), type='EVENT_SYSTEM')
            self.app.gameevents.add("calibration", "stop", "", type='EVENT_SYSTEM')
            self.app.state = self.post_calibrate_mode
    
        def calibrate(self, changeState):
            self.startDataStreaming()
            if changeState:
                self.post_calibrate_mode = self.app.state
                self.app.state = self.app.STATE_CALIBRATE
            self.app.gameevents.add("calibration", "start", "", type='EVENT_SYSTEM')
            self.calibrator.start(self.calibrationDone, self.post_calibrate_mode)
    
        def eventCallback(self, *args, **kwargs):
    
            if args[3] == 'config' and args[4] == 'load':
    
                if args[5] == 'defaults':
    
                    self.app.config.add_setting(self.name, 'enabled', False, type=2, alias="Enable", about='Enable eye tracking using PyViewX')
                    self.app.config.add_setting(self.name, 'server_address', '127.0.0.1', type=3, alias="Address", about='iViewX Server Address')
                    self.app.config.add_setting(self.name, 'server_inport', '5555', type=3, alias="Incoming Port", about='iViewX Server Incoming Port')
                    self.app.config.add_setting(self.name, 'server_outport', '4444', type=3, alias="Outgoing Port", about='iViewX Server Outgoing Port')
                    self.app.config.add_setting(self.name, 'calmode', 'Once', type=1, alias='When To Calibrate', options=['Every Game', 'Once'], about='Set when eye tracker is calibrated')
    
            elif args[3] == 'display':
    
                if args[4] == 'setmode':
                    if self.client:
                        self.calibrator = Calibrator(self.client, self.app.screen, reactor=self.app.reactor)
                        if self.app.config[self.name]['calmode'] == 'Once':
                            self.app.reactor.callLater(1, self.calibrate, False)
    
            elif args[3] == 'game':
    
                if args[4] == 'ready':
                    if self.client and self.app.config[self.name]['calmode'] == 'Every Game':
                        self.calibrate(True)

except ImportError as e:
    sys.stderr.write("Failed to load 'PyViewX' plugin, missing dependencies. [%s]\n" % e)
