"""
Cogworks Subject Info
"""

try:
    
    import sys, os

    from PySide.QtCore import *
    from PySide.QtGui import *

    from pycogworks.gui import *
    from pycogworks.crypto import rin2id

    class SF5Plugin(object):

        def __init__(self, app):
            super(SF5Plugin, self).__init__()
            self.app = app
            self.subjectInfo = None
            self.expRoom = None

        def eventCallback(self, *args, **kwargs):

            if args[3] == 'config' and args[4] == 'load':

                if args[5] == 'defaults':

                    self.app.config.add_setting('CogWorks Exp', 'subject_window', False, type=2, about='Prompt for subject information')
                    self.app.config.add_setting('CogWorks Exp', 'experiment_room', '', type=3, about='Write history file')
                    self.app.config.add_setting('CogWorks Exp', 'subdir', True, type=2, about='Put subject data in their own subdirs based on eid.')

                elif args[5] == 'user':

                    if self.app.config['CogWorks Exp']['subject_window']:

                        self.subjectInfo = getSubjectInfo([])
                        if self.subjectInfo:
                            eid = rin2id(self.subjectInfo['rin'])
                            self.app.config.update_setting_value("General", "id", eid[:8])
                            if self.app.config['CogWorks Exp']['subdir']:
                                self.app.config.update_setting_value('Logging', 'logdir', os.path.join(self.app.config[ 'Logging']['logdir'], eid[:8]))
                        else:
                            sys.exit()

                    self.expRoom = self.app.config['CogWorks Exp']['experiment_room'].strip()

            elif args[3] == 'log':

                if args[4] == 'basename' and args[5] == 'ready':
                    if self.app.config['CogWorks Exp']['subject_window'] and self.subjectInfo:
                        eid = rin2id(self.subjectInfo['rin'])
                        self.subjectInfo['encrypted_rin'] = eid
                        self.subjectInfo['cipher'] = 'AES/CBC (RIJNDAEL) - 16Byte Key'
                        writeHistoryFile(self.app.log_basename, self.subjectInfo)

                elif args[4] == 'header' and args[5] == 'ready':
                    if self.app.config['CogWorks Exp']['subject_window']:
                        self.app.gameevents.add("participant", "encrypted_rin", self.subjectInfo['encrypted_rin'], type='EVENT_SYSTEM')
                    if self.expRoom and len(self.expRoom) > 0:
                        self.app.gameevents.add("experiment", "room", self.expRoom, type='EVENT_SYSTEM')


except ImportError as e:
    sys.stderr.write("Failed to load 'CWSubject' plugin, missing dependencies. [%s]\n" % e)
