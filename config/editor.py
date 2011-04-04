#!/usr/bin/env python

import sys

from PySide.QtCore import *
from PySide.QtGui import *

CT_LINEEDIT = 0
CT_COMBO = 1
CT_CHECKBOX = 2
CT_SPINBOX = 3
CT_DBLSPINBOX = 4

class SpinBox(QSpinBox):
    
    def __init__(self, config, category, setting, info):
        super(SFSpinBox, self).__init__()
        self.config = config
        self.category = category
        self.setting = setting
        self.info = info
        self.setMaximum(1000000)
        self.setValue(info['value'])
        QObject.connect(self, SIGNAL('valueChanged(int)'), self.stateChangeHandler)
            
    def stateChangeHandler(self, newVal):
        self.config.update_setting_value(self.category, self.setting, newVal)
    
class CheckBox(QCheckBox):
    
    def __init__(self, config, category, setting, info):
        super(SFCheckBox, self).__init__()
        self.config = config
        self.category = category
        self.setting = setting
        self.info = info
        if info['value']:
            self.setCheckState(Qt.Checked)
        else:
            self.setCheckState(Qt.Unchecked)
        QObject.connect(self, SIGNAL('stateChanged(int)'), self.stateChangeHandler)
            
    def stateChangeHandler(self, newVal):
        if newVal == Qt.Checked:
            self.config.update_setting_value(self.category, self.setting, True)
        else:
            self.config.update_setting_value(self.category, self.setting, False)
            
class LineEdit(QLineEdit):
    
    def __init__(self, config, category, setting, info):
        super(SFLineEdit, self).__init__()
        self.config = config
        self.category = category
        self.setting = setting
        self.info = info
        self.setText(str(info['value']))
        if info.has_key('n'):
            self.setMaxLength(info['n'])
            self.setFixedWidth(info['n']*self.minimumSizeHint().height())
        QObject.connect(self, SIGNAL('textChanged(QString)'), self.stateChangeHandler)
            
    def stateChangeHandler(self, newVal):
        self.config.update_setting_value(self.category, self.setting, newVal)
    
class ConfigEditor(QMainWindow):
    
    def __init__(self, cfg, title='Config Editor'):
        super(ConfigEditor, self).__init__()
        
        self.config = cfg
        
        self.categories = QListWidget()
        self.settings = QStackedWidget()
        
        self.setFixedSize(640,420)
        self.categories.setMaximumWidth(120)
        
        QObject.connect(self.categories, SIGNAL('itemSelectionChanged()'), self.category_selected)
        
        for cat in self.config.get_categories():
            self.categories.addItem(cat)
            settings_layout = QGridLayout()
            r = 0
            c = 0
            for setting in self.config.get_settings(cat):
                info = self.config.get_setting(cat, setting, True)
                s = QWidget()
                sl = QVBoxLayout()
                sl.setAlignment(Qt.AlignLeft)
                sl.addWidget(QLabel(setting))
                if info['type'] == CT_LINEEDIT:
                    w = SFLineEdit(self.config,cat,setting,info)
                elif info['type'] == CT_CHECKBOX:
                    w = SFCheckBox(self.config,cat,setting,info)
                elif info['type'] == CT_SPINBOX:
                    w = SFSpinBox(self.config,cat,setting,info)
                elif info['type'] == CT_COMBO:
                    w = SFComboBox(self.config,cat,setting,info)
                sl.addWidget(w)
                s.setLayout(sl)
                c = self.config.config[cat].index(setting) % 2
                settings_layout.addWidget(s, r, c)
                if c == 1:
                    r += 1
            settings = QWidget()
            settings.setLayout(settings_layout)
            settings_scroller = QScrollArea()
            settings_scroller.setAlignment(Qt.AlignHCenter)
            settings_scroller.setWidget(settings)
            self.settings.addWidget(settings_scroller)
        
        self.main = QWidget()
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.categories)
        self.main_layout.addWidget(self.settings)
        self.main.setLayout(self.main_layout)
        
        self.setCentralWidget(self.main)
        self.setWindowTitle(title)
        self.setUnifiedTitleAndToolBarOnMac(True)
        
        self.categories.setCurrentItem(self.categories.item(0))
        
        self.menuBar = QMenuBar()
        self.filemenu = QMenu('&File')
        self.quitAction = QAction(self)
        self.quitAction.setText('&Quit')
        if platform.system() != 'Darwin':
            self.quitAction.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Q))
        QObject.connect(self.quitAction, SIGNAL('triggered()'), self.quitApp)
        self.filemenu.addAction(self.quitAction)
        self.menuBar.addMenu(self.filemenu)
        self.setMenuBar(self.menuBar)
        
        self.show()
        self.activateWindow()
        self.raise_()
        
        screen = QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        
    def category_selected(self):
        self.settings.setCurrentIndex(self.config.config.index(self.categories.selectedItems()[0].text()))
        
    def quitApp(self):
        app.closeAllWindows()
        
    def closeEvent(self, event=None):
        config = diff_config(self.config)
        if config == False:
            delete_config()
        elif config != None:
            save_config(config)
        self.quitApp()
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = ConfigEditor('Spacefortress Config Editor')
    sys.exit(app.exec_())
    
