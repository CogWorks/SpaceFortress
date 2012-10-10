"""
Playback helper
"""

import sys

from PySide.QtCore import *
from PySide.QtGui import *

app = QApplication(sys.argv)

class GamePicker(QDialog):
    
    def __init__(self, ngames):
        super(GamePicker, self).__init__()
        
        self.value = 0
        
        self.setModal(True)
    
        self.main_layout = QVBoxLayout()
        
        self.gamelayout = QHBoxLayout()
        self.games = QLabel('Playback Game:')
        self.spinbox = QSpinBox()
        self.spinbox.setMinimum(1)
        self.spinbox.setMaximum(ngames)
        self.gamelayout.addWidget(self.games)
        self.gamelayout.addWidget(self.spinbox)
        
        self.mainButtons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.ok = self.mainButtons.button(QDialogButtonBox.StandardButton.Ok)
        self.cancel = self.mainButtons.button(QDialogButtonBox.StandardButton.Cancel)
        QObject.connect(self.mainButtons, SIGNAL('clicked(QAbstractButton *)'), self.mainbutton_clicked)
        
        self.main_layout.addLayout(self.gamelayout)
        self.main_layout.addWidget(self.mainButtons)
        
        self.setLayout(self.main_layout)
        
        self.setWindowTitle('Pick A Game')
        
        self.show()
        self.activateWindow()
        self.raise_()
        
        self.setMinimumWidth(self.geometry().width() * 1.25)
        
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)
    
    def mainbutton_clicked(self, button):
        if button == self.ok:
            self.value = self.spinbox.value()
            self.setResult(True)
            self.done(True)
        elif button == self.cancel:
            self.setResult(False)
            self.done(True)
            
def pickGame(ngames):
    gp = GamePicker(ngames)
    app.exec_()
    return gp.value

def pickLog():
    return QFileDialog.getOpenFileName(None, caption='Pick Log File', filter='Space Fortress Log (*.txt)')[0]

if __name__ == '__main__':
    print pickLog()
    print pickGame(5)
