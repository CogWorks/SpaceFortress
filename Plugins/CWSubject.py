"""
Cogworks Subject Info
"""

import sys

from PySide.QtCore import *
from PySide.QtGui import *

class SubjectWindow(QDialog):
    
    def __init__(self, app):
        super(SubjectWindow, self).__init__()
        self.app = app
        
        self.values = None
        
        self.setModal(True)
    
        self.main_layout = QVBoxLayout()
        
        self.settings_layout = QGridLayout()
        
        self.settings_layout.addWidget(QLabel('First Name'), 0, 0)
        self.first_name = QLineEdit()
        self.settings_layout.addWidget(self.first_name, 0, 1)
        
        self.settings_layout.addWidget(QLabel('Last Name'), 1, 0)
        self.last_name = QLineEdit()
        self.settings_layout.addWidget(self.last_name, 1, 1)
        
        self.settings_layout.addWidget(QLabel('RIN'), 2, 0)
        self.rin = QLineEdit()
        self.rin.setMaxLength(9)
        QObject.connect(self.rin, SIGNAL('textChanged(const QString&)'), self.rin_changed)
        self.settings_layout.addWidget(self.rin, 2, 1)
        
        self.settings_layout.addWidget(QLabel('Age'), 3, 0)
        self.age = QLineEdit()
        self.settings_layout.addWidget(self.age, 3, 1)
        
        self.settings_layout.addWidget(QLabel('Gender'), 4, 0)
        self.gender = QLineEdit()
        self.settings_layout.addWidget(self.gender, 4, 1)
        
        self.settings_layout.addWidget(QLabel('Major'), 5, 0)
        self.major = QLineEdit()
        self.settings_layout.addWidget(self.major, 5, 1)
        
        self.mainButtons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.ok = self.mainButtons.button(QDialogButtonBox.StandardButton.Ok)
        self.ok.setEnabled(False)
        self.cancel = self.mainButtons.button(QDialogButtonBox.StandardButton.Cancel)
        QObject.connect(self.mainButtons, SIGNAL('clicked(QAbstractButton *)'), self.mainbutton_clicked)
        
        
        self.main_layout.addLayout(self.settings_layout)
        self.main_layout.addWidget(self.mainButtons)
        
        self.setLayout(self.main_layout)
        
        self.setWindowTitle('Participant Information')
        #self.setSizeGripEnabled(False)
        
        self.show()
        self.activateWindow()
        self.raise_()
        
        self.setMinimumWidth(self.geometry().width()*1.2)
        
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        
    def rin_changed(self, rin):
        if len(rin) == 9:
            try:
                if int(rin) > 0:
                    self.ok.setEnabled(True)
            except ValueError:
                pass
        else:
            self.ok.setEnabled(False)
    
    def mainbutton_clicked(self, button):
        if button == self.ok:
            self.values = (self.first_name.text(),self.last_name.text(),self.rin.text(),self.age.text(),self.gender.text(),self.major.text())
            self.setResult(True)
            self.done(True)
        elif button == self.cancel:
            self.setResult(False)
            self.done(True)
            
def getSubjectInfo():
    app = QApplication(sys.argv)
    sw = SubjectWindow(app)
    app.exec_()
    return sw.values

class SF5Plugin(object):
    
    def __init__(self, app):
        super(SF5Plugin, self).__init__()
        self.app = app
        self.subjectInfo = None
    
    def eventCallback(self, *args, **kwargs):
        
        if args[3] == 'config' and args[4] == 'load':
            
            if args[5] == 'defaults':
            
                self.app.config.add_setting('CogWorks Subject', 'subject_window', False, type=2, about='Prompt for subject information')
                    
            elif args[5] == 'user':
                
                if self.app.config.get_setting('CogWorks Subject','subject_window'):
                
                    self.subjectInfo = getSubjectInfo()
                    if self.subjectInfo:
                        self.app.config.update_setting_value("General","id",int(self.subjectInfo[2]))
            
        elif args[3] == 'log' and args[4] == 'ready':
            
            pass
        
if __name__ == '__main__':
    print getSubjectInfo()