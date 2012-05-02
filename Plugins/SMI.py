"""
PyViewX Integration
"""
import pygame
import numpy as np
from pyviewx import iViewXClient, Dispatcher
from pyviewx.pygamesupport import Calibrator

class SF5Plugin( object ):

    d = Dispatcher()

    header = ["gazetime","gaze_type","left_gaze_x","right_gaze_x","left_gaze_y","right_gaze_y",
              "left_pupil_x","right_pupil_x","left_pupil_y","right_pupil_y",
              "left_eye_x","right_eye_x","left_eye_y","right_eye_y","left_eye_z","right_eye_z"]

    def __init__( self, app ):
        super( SF5Plugin, self ).__init__()
        self.app = app
        self.client = None
        self.post_calibrate_mode = -1
        self.eye_data = None
        self.null_data = "\t" + "\t".join( ["NA"] * len( self.header ) )

    def ready( self ):
        if self.app.config.get_setting( 'PyViewX', 'enabled' ):
            self.client = iViewXClient( self.app.config.get_setting( 'PyViewX', 'server_address' ), int( self.app.config.get_setting( 'PyViewX', 'server_outport' ) ) )
            self.client.addDispatcher( self.d )
            if self.client:
                if self.app.config.get_setting( 'PyViewX', 'calmode' ) == 'Once':
                    self.post_calibrate_mode = self.app.state
                    self.app.state = self.app.STATE_CALIBRATE
                self.app.reactor.listenUDP( int( self.app.config.get_setting( 'PyViewX', 'server_inport' ) ), self.client )
                self.startDataStreaming()

    def logHeader(self):
        if self.client:
            return '\t' + '\t'.join(self.header)
        else:
            return None

    def logCallback(self):
        if self.eye_data:
            return self.eye_data
        else:
            return self.null_data

    @d.listen( 'ET_SPL' )
    def iViewXEvent( self, inSender, inEvent, inResponse ):
        self.eye_data = inResponse

    def startDataStreaming( self ):
        self.client.setDataFormat( '%TS %ET %SX %SY %DX %DY %EX %EY %EZ' )
        self.client.startDataStreaming()

    def stopDataStreaming( self ):
        self.client.stopDataStreaming()

    def calibrationDone( self, lc, post_calibrate_mode ):
        self.app.state = post_calibrate_mode

    def calibrate( self, changeState ):
        self.startDataStreaming()
        if changeState:
            self.post_calibrate_mode = self.app.state
            self.app.state = self.app.STATE_CALIBRATE
        self.calibrator.start( self.calibrationDone, self.post_calibrate_mode )

    def eventCallback( self, *args, **kwargs ):

        if args[3] == 'config' and args[4] == 'load':

            if args[5] == 'defaults':

                self.app.config.add_setting( 'PyViewX', 'enabled', False, type = 2, alias = "Enable", about = 'Enable eye tracking using PyViewX' )
                self.app.config.add_setting( 'PyViewX', 'server_address', '127.0.0.1', type = 3, alias = "Address", about = 'iViewX Server Address' )
                self.app.config.add_setting( 'PyViewX', 'server_inport', '5555', type = 3, alias = "Incoming Port", about = 'iViewX Server Incoming Port' )
                self.app.config.add_setting( 'PyViewX', 'server_outport', '4444', type = 3, alias = "Outgoing Port", about = 'iViewX Server Outgoing Port' )
                self.app.config.add_setting( 'PyViewX', 'calmode', 'Once', type = 1, alias = 'When To Calibrate', options = ['Every Game', 'Once'], about = 'Set when eye tracker is calibrated' )

        elif args[3] == 'display':

            if args[4] == 'setmode':
                if self.client:
                    self.calibrator = Calibrator( self.client, self.app.screen, reactor = self.app.reactor )
                    if self.app.config.get_setting( 'PyViewX', 'calmode' ) == 'Once':
                        self.app.reactor.callLater(1, self.calibrate, False)

        elif args[3] == 'game':

            if args[4] == 'ready':
                if self.client and self.app.config.get_setting( 'PyViewX', 'calmode' ) == 'Every Game':
                    self.calibrate( True )
