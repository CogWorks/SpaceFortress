#!/usr/bin/env python

import sys, os, copy, platform, json

from PySide.QtCore import *
from PySide.QtGui import *

from __init__ import Config, MyEncoder
import constants
    
class ComboBox(QComboBox):
    
    def __init__(self, editor, config, category, setting, info):
        super(ComboBox, self).__init__()
        self.editor = editor
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
        
    def updateValue(self, newVal):
        for i in range(0,len(self.info['options'])):
            if self.info['options'][i] == newVal:
                self.setCurrentIndex(i)
            
    def stateChangeHandler(self, newVal):
        for i in range(0,len(self.info['options'])):
            if self.info['options'][i] == self.info['value']:
                self.cfg.update_setting_value(self.category, self.setting, self.info['options'][newVal])
        self.editor.dirty_check()

class DoubleSpinBox(QDoubleSpinBox):
    
    def __init__(self, editor, config, category, setting, info):
        super(DoubleSpinBox, self).__init__()
        self.editor = editor
        self.cfg = config
        self.category = category
        self.setting = setting
        self.info = info
        self.setMaximum(1000000)
        self.setValue(info['value'])
        QObject.connect(self, SIGNAL('valueChanged(double)'), self.stateChangeHandler)
        
    def updateValue(self, newVal):
        self.setValue(newVal)
            
    def stateChangeHandler(self, newVal):
        self.cfg.update_setting_value(self.category, self.setting, newVal)
        self.editor.dirty_check()
        
class SpinBox(QSpinBox):
    
    def __init__(self, editor, config, category, setting, info):
        super(SpinBox, self).__init__()
        self.editor = editor
        self.cfg = config
        self.category = category
        self.setting = setting
        self.info = info
        self.setMaximum(1000000)
        self.setValue(info['value'])
        QObject.connect(self, SIGNAL('valueChanged(int)'), self.stateChangeHandler)
        
    def updateValue(self, newVal):
        self.setValue(newVal)
            
    def stateChangeHandler(self, newVal):
        self.cfg.update_setting_value(self.category, self.setting, newVal)
        self.editor.dirty_check()
    
class CheckBox(QCheckBox):
    
    def __init__(self, editor, config, category, setting, info):
        super(CheckBox, self).__init__()
        self.editor = editor
        self.cfg = config
        self.category = category
        self.setting = setting
        self.info = info
        if info['value']:
            self.setCheckState(Qt.Checked)
        else:
            self.setCheckState(Qt.Unchecked)
        QObject.connect(self, SIGNAL('stateChanged(int)'), self.stateChangeHandler)
        
    def updateValue(self, newVal):
        if newVal:
            self.setCheckState(Qt.Checked)
        else:
            self.setCheckState(Qt.Unchecked)
            
    def stateChangeHandler(self, newVal):
        if newVal == Qt.Checked:
            self.cfg.update_setting_value(self.category, self.setting, True)
        else:
            self.cfg.update_setting_value(self.category, self.setting, False)
        self.editor.dirty_check()
            
class LineEdit(QLineEdit):
    
    def __init__(self, editor, config, category, setting, info):
        super(LineEdit, self).__init__()
        self.editor = editor
        self.cfg = config
        self.category = category
        self.setting = setting
        self.info = info
        self.setText(str(info['value']))
        if info.has_key('n'):
            self.setMaxLength(info['n'])
            self.setFixedWidth(info['n']*self.minimumSizeHint().height())
        QObject.connect(self, SIGNAL('textChanged(QString)'), self.stateChangeHandler)
        
    def updateValue(self, newVal):
        self.setText(newVal)
            
    def stateChangeHandler(self, newVal):
        self.cfg.update_setting_value(self.category, self.setting, newVal)
        self.editor.dirty_check()
    
class ConfigEditor(QMainWindow):
    
    def __init__(self, app, cfg, title='Config Editor'):
        super(ConfigEditor, self).__init__()
        
        self.app = app
        self.cfg = cfg
        
        self.dirty = False
        
        self.def_cfg = copy.deepcopy(self.cfg)
        self.cfg.update_from_user_file()
        self.base_cfg = copy.deepcopy(self.cfg)
        
        self.categories = QListWidget()
        #self.categories.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Expanding)
        self.settings = QStackedWidget()
        #self.categories.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Expanding)
        
        QObject.connect(self.categories, SIGNAL('itemSelectionChanged()'), self.category_selected)
        
        self.widget_list = {}
        for cat in self.cfg.get_categories():
            self.widget_list[cat] = {}
        longest_cat = 0
        for cat in self.cfg.get_categories():
            if len(cat) > longest_cat:
                longest_cat = len(cat)
            self.categories.addItem(cat)
            settings_layout = QGridLayout()
            r = 0
            c = 0
            for setting in self.cfg.get_settings(cat):
                info = self.cfg.get_setting(cat, setting, True)
                s = QWidget()
                s.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
                sl = QVBoxLayout()
                label = QLabel()
                if info.has_key('alias'):
                    label.setText(info['alias'])
                else:
                    label.setText(setting)
                if info.has_key('about'):
                    label.setToolTip(info['about'])
                sl.addWidget(label)
                if info['type'] == constants.CT_LINEEDIT:
                    w = LineEdit(self, self.cfg,cat,setting,info)
                elif info['type'] == constants.CT_CHECKBOX:
                    w = CheckBox(self, self.cfg,cat,setting,info)
                elif info['type'] == constants.CT_SPINBOX:
                    w = SpinBox(self, self.cfg,cat,setting,info)
                elif info['type'] == constants.CT_DBLSPINBOX:
                    w = DoubleSpinBox(self, self.cfg,cat,setting,info)
                elif info['type'] == constants.CT_COMBO:
                    w = ComboBox(self, self.cfg,cat,setting,info)
                w.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
                self.widget_list[cat][setting] = w
                sl.addWidget(w)
                s.setLayout(sl)
                c = self.cfg.config[cat].index(setting) % 2
                settings_layout.addWidget(s, r, c)
                if c == 1:
                    r += 1
            settings = QWidget()
            settings.setLayout(settings_layout)
            settings_scroller = QScrollArea()
            settings_scroller.setWidget(settings)
            settings_scroller.setWidgetResizable(True)
            self.settings.addWidget(settings_scroller)
            
        font = self.categories.font()
        fm = QFontMetrics(font)
        self.categories.setMaximumWidth(fm.widthChar('X')*(longest_cat+4))
        
        self.main = QWidget()
        self.main_layout = QVBoxLayout()
        
        self.config_layout = QHBoxLayout()
        self.config_layout.addWidget(self.categories)
        self.config_layout.addWidget(self.settings)
        
        self.mainButtons = QDialogButtonBox(QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Reset | QDialogButtonBox.Apply)
        self.main_apply = self.mainButtons.button(QDialogButtonBox.StandardButton.Apply)
        self.main_reset = self.mainButtons.button(QDialogButtonBox.StandardButton.Reset)
        self.main_defaults = self.mainButtons.button(QDialogButtonBox.StandardButton.LastButton)
        QObject.connect(self.mainButtons, SIGNAL('clicked(QAbstractButton *)'), self.mainbutton_clicked)
        
        self.dirty_check()
        
        self.main_layout.addLayout(self.config_layout)
        self.main_layout.addWidget(self.mainButtons)
        
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
        
        self.setMinimumWidth(self.geometry().width()*1.2)
        
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        
    def category_selected(self):
        self.settings.setCurrentIndex(self.cfg.config.index(self.categories.selectedItems()[0].text()))
        
    def mainbutton_clicked(self, button):
        if button == self.main_reset:
            for cat in self.base_cfg.get_categories():
                for setting in self.base_cfg.get_settings(cat):
                    self.widget_list[cat][setting].updateValue(self.base_cfg.get_setting(cat,setting))
        elif button == self.main_defaults:
            for cat in self.def_cfg.get_categories():
                for setting in self.def_cfg.get_settings(cat):
                    self.widget_list[cat][setting].updateValue(self.def_cfg.get_setting(cat,setting))
        elif button == self.main_apply:
            bad_settings = self.validate_settings()
            if bad_settings == []:
                self.save_settings()
                self.main_apply.setEnabled(False)
                self.main_reset.setEnabled(False)
            else:
                msgBox = QMessageBox()
                msgBox.setText("Must fix the following invalid settings before quitting:")
                msgBox.setStandardButtons(QMessageBox.Ok)
                info = ''
                for setting in bad_settings:
                    new = '%s,%s<br>' % setting
                    info = '%s%s' % (info, new)
                msgBox.setInformativeText(info)
                msgBox.exec_()
            
        
    def quitApp(self):
        self.app.closeAllWindows()
        
    def get_changes(self):
        enc = MyEncoder()
        if enc.encode(self.def_cfg.config) == enc.encode(self.cfg.config):
            return False
        if enc.encode(self.base_cfg.config) != enc.encode(self.cfg.config):
            newC = Config()
            for c in self.cfg.config.keys():
                for s in self.cfg.config[c].keys():
                    if self.cfg.config[c][s]['value'] != self.def_cfg.config[c][s]['value']:
                        newC.add_setting(c, s, self.cfg.config[c][s]['value'], stub=True)    
            return json.dumps(newC.config, separators=(',',': '), indent=4, sort_keys=True)
        else:
            return None
        
    def validate_settings(self):
        ret = []
        for cat in self.cfg.get_categories():
            for setting in self.cfg.get_settings(cat):
                info = self.cfg.get_setting(cat, setting, True)
                if info.has_key('validate'):
                    if not info['validate'](info):
                        ret.append((cat,setting))
        return ret
    
    def dirty_check(self):
        if str(self.base_cfg) != str(self.cfg):
            self.dirty = True
            self.main_apply.setEnabled(True)
            self.main_reset.setEnabled(True)
        else:
            self.dirty = False
            self.main_apply.setEnabled(False)
            self.main_reset.setEnabled(False)
        if str(self.def_cfg) == str(self.cfg):
            self.main_defaults.setEnabled(False)
        else:
            self.main_defaults.setEnabled(True)
            
    def save_settings(self):
        config = self.get_changes()
        if config == False:
            if os.path.isfile(self.cfg.user_file):
                os.remove(self.cfg.user_file)
        elif config != None:
            with open(self.cfg.user_file, 'w+') as f:
                f.write(config)
        self.base_cfg = copy.deepcopy(self.cfg)
            
    def closeEvent(self, event=None):
        self.quitApp()
    
