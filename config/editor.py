#!/usr/bin/env python

import sys, os, copy, platform, json

from PySide.QtCore import *
from PySide.QtGui import *

from __init__ import Config

CT_LINEEDIT = 0
CT_COMBO = 1
CT_CHECKBOX = 2
CT_SPINBOX = 3
CT_DBLSPINBOX = 4
    
class ComboBox(QComboBox):
    
    def __init__(self, config, category, setting, info):
        super(ComboBox, self).__init__()
        self.cfg = config
        self.category = category
        self.setting = setting
        self.info = info
        if info.has_key('options'):
            self.addItems(info['options'])
            for i in range(0,len(info['options'])):
                if info['options'][i] == info['value']:
                    self.setCurrentIndex(i)
        QObject.connect(self, SIGNAL('currentIndexChanged(int)'), self.stateChangeHandler)
            
    def stateChangeHandler(self, newVal):
        for i in range(0,len(self.info['options'])):
            if self.info['options'][i] == self.info['value']:
                self.cfg.update_setting_value(self.category, self.setting, self.info['options'][newVal])

class SpinBox(QSpinBox):
    
    def __init__(self, config, category, setting, info):
        super(SpinBox, self).__init__()
        self.cfg = config
        self.category = category
        self.setting = setting
        self.info = info
        self.setMaximum(1000000)
        self.setValue(info['value'])
        QObject.connect(self, SIGNAL('valueChanged(int)'), self.stateChangeHandler)
            
    def stateChangeHandler(self, newVal):
        self.cfg.update_setting_value(self.category, self.setting, newVal)
    
class CheckBox(QCheckBox):
    
    def __init__(self, config, category, setting, info):
        super(CheckBox, self).__init__()
        self.cfg = config
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
            self.cfg.update_setting_value(self.category, self.setting, True)
        else:
            self.cfg.update_setting_value(self.category, self.setting, False)
            
class LineEdit(QLineEdit):
    
    def __init__(self, config, category, setting, info):
        super(LineEdit, self).__init__()
        self.cfg = config
        self.category = category
        self.setting = setting
        self.info = info
        self.setText(str(info['value']))
        if info.has_key('n'):
            self.setMaxLength(info['n'])
            self.setFixedWidth(info['n']*self.minimumSizeHint().height())
        QObject.connect(self, SIGNAL('textChanged(QString)'), self.stateChangeHandler)
            
    def stateChangeHandler(self, newVal):
        self.cfg.update_setting_value(self.category, self.setting, newVal)
    
class ConfigEditor(QMainWindow):
    
    def __init__(self, app, cfg, title='Config Editor'):
        super(ConfigEditor, self).__init__()
        
        self.app = app
        self.cfg = cfg
        
        self.def_cfg = copy.deepcopy(self.cfg)
        self.cfg.update_from_user_file()
        self.base_cfg = copy.deepcopy(self.cfg)
        
        self.categories = QListWidget()
        self.settings = QStackedWidget()
        
        self.setFixedSize(640,420)
        self.categories.setMaximumWidth(120)
        
        QObject.connect(self.categories, SIGNAL('itemSelectionChanged()'), self.category_selected)
        
        for cat in self.cfg.get_categories():
            self.categories.addItem(cat)
            settings_layout = QGridLayout()
            r = 0
            c = 0
            for setting in self.cfg.get_settings(cat):
                info = self.cfg.get_setting(cat, setting, True)
                s = QWidget()
                sl = QVBoxLayout()
                sl.setAlignment(Qt.AlignLeft)
                sl.addWidget(QLabel(setting))
                if info['type'] == CT_LINEEDIT:
                    w = LineEdit(self.cfg,cat,setting,info)
                elif info['type'] == CT_CHECKBOX:
                    w = CheckBox(self.cfg,cat,setting,info)
                elif info['type'] == CT_SPINBOX:
                    w = SpinBox(self.cfg,cat,setting,info)
                elif info['type'] == CT_COMBO:
                    w = ComboBox(self.cfg,cat,setting,info)
                sl.addWidget(w)
                s.setLayout(sl)
                c = self.cfg.config[cat].index(setting) % 2
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
        self.settings.setCurrentIndex(self.cfg.config.index(self.categories.selectedItems()[0].text()))
        
    def quitApp(self):
        self.app.closeAllWindows()
        
    def get_changes(self):
        if json.dumps(self.def_cfg.config) == json.dumps(self.cfg.config):
            return False
        if json.dumps(self.base_cfg.config) != json.dumps(self.cfg.config):
            newC = Config()
            for c in self.cfg.config.keys():
                for s in self.cfg.config[c].keys():
                    if self.cfg.config[c][s]['value'] != self.def_cfg.config[c][s]['value']:
                        newC.add_setting(c, s, self.cfg.config[c][s]['value'], stub=True)    
            return json.dumps(newC.config, separators=(',',': '), indent=4, sort_keys=True)
        else:
            return None
        
    def closeEvent(self, event=None):
        config = self.get_changes()
        if config == False:
            if os.path.isfile(self.cfg.user_file):
                os.remove(self.cfg.user_file)
        elif config != None:
            with open(self.cfg.user_file, 'w+') as f:
                f.write(config)
        self.quitApp()
    
