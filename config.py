#!/usr/bin/env python

import sys, os, platform, json, copy
from pythonutils.odict import OrderedDict
from PySide.QtCore import *
from PySide.QtGui import *

CT_LINEEDIT = 0
CT_COMBO = 1
CT_CHECKBOX = 2
CT_SPINBOX = 3
CT_DBLSPINBOX = 4

PYGAME_KEYS = ['1','2','3','4','5','6','7','8','9','0',
               'q','w','e','r','t','y','u','i','o','p',
               'a','s','d','f','g','h','j','k','l',
               'z','x','c','v','b','n','m','SPACE',
               'BACKSPACE','TAB','RETURN','COMMA','MINUS','PERIOD',
               'SLASH','SEMICOLON','QUOTE','LEFTBRACKET','RIGHTBRACKET',
               'BACKSLASH','EQUALS','BACKQUOTE','UP','DOWN','RIGHT','LEFT']

def get_config_home():
    _home = os.environ.get('HOME', '/')
    if platform.system() == 'Windows':
        config_home = os.path.join(os.environ['APPDATA'], 'SpaceFortress')
    elif platform.system() == 'Linux':
        config_home = os.path.join(os.environ.get('XDG_CONFIG_HOME', os.path.join(_home, '.config')), 'spacefortress')
    elif platform.system() == 'Darwin':
        config_home = os.path.join(_home, 'Library', 'Application Support', 'SpaceFortress')
    else:
        config_home = os.path.join(_home, '.spacefortress')
    if not os.path.exists(config_home):
        os.makedirs(config_home)
    return config_home

class Config():
        
    def add_category(self, category):
        if not self.config.has_key(category):
            self.config[category] = OrderedDict()
            
    def add_setting(self, category, setting, value, about='', type=CT_SPINBOX, **kwargs):
        assert category!=None, 'Must specify a category'
        assert setting!=None, 'Must specify a setting'
        assert value!=None, 'Must specify a value'
        self.add_category(category)
        if not self.config[category].has_key(setting):
            self.config[category][setting] = OrderedDict()
        self.config[category][setting]['value'] = value
        self.config[category][setting]['about'] = about
        self.config[category][setting]['type'] = type
        for k in kwargs:
            self.config[category][setting][k] = kwargs[k]
        
    def get_setting(self, category, setting, complete=False):
        assert category!=None, 'Must specify a category'
        assert setting!=None, 'Must specify a setting'
        assert self.config.has_key(category), 'Category does not exist'
        assert self.config[category].has_key(setting), 'Setting in category does not exist'
        assert self.config[category][setting].has_key('value'), 'Setting in category has no value'
        if complete:
            return self.config[category][setting]
        else:
            return self.config[category][setting]['value']
        
    def update_setting_value(self, category, setting, value):
        assert category!=None, 'Must specify a category'
        assert setting!=None, 'Must specify a setting'
        assert value!=None, 'Must specify a value'
        if self.config.has_key(category):
            if self.config[category].has_key(setting):
                self.config[category][setting]['value'] = value
    
    def get_settings(self, category):
        assert category!=None, 'Must specify a category'
        assert self.config.has_key(category), 'Category does not exist'
        return self.config[category].keys()
    
    def get_categories(self):
        return self.config.keys()
        
    def __init__(self, defaults=True, load=True):
        
        self.config = OrderedDict()
        
        if defaults:

            self.add_setting('General', 'human', True, type=CT_CHECKBOX, about='Will this game be played by a human or a cognitive model? Set to f to disable human control, enabling ACT-R')
            self.add_setting('General', 'fullscreen', False, type=CT_CHECKBOX, about='Run at full screen? Set to f to run in a window')
            self.add_setting('General', 'linewidth', 1, 'Width of lines drawn on screen. Increase for a more "projector-friendly" game')
            self.add_setting('General', 'psf', False, type=CT_CHECKBOX, about='Original PSF (SF4) settings? If t, *ALL* further values are ignored')
            self.add_setting('General', 'game_time', 30000, 'Time in milliseconds for a game. NOTE! If you escape in the middle of a game, the log will have "short" prepended to the name')
            self.add_setting('General', 'games_per_session', 8, 'Number of games per "session"')
            self.add_setting('General', 'print_events', False, type=CT_CHECKBOX, about='Print events to stdout')
            self.add_setting('General', 'sound', True, type=CT_CHECKBOX, about='Enable/disable sound')
            
            self.add_setting('Keybindings', 'thrust_key', 'w', type=CT_COMBO, options=PYGAME_KEYS)
            self.add_setting('Keybindings', 'left_turn_key', 'a', type=CT_COMBO, options=PYGAME_KEYS)
            self.add_setting('Keybindings', 'right_turn_key', 'd', type=CT_COMBO, options=PYGAME_KEYS)
            self.add_setting('Keybindings', 'fire_key', 'SPACE', type=CT_COMBO, options=PYGAME_KEYS)
            self.add_setting('Keybindings', 'IFF_key', 'j', type=CT_COMBO, options=PYGAME_KEYS)
            self.add_setting('Keybindings', 'shots_key', 'k', type=CT_COMBO, options=PYGAME_KEYS)
            self.add_setting('Keybindings', 'pnts_key', 'l', type=CT_COMBO, options=PYGAME_KEYS)
            
            self.add_setting('Ship', 'ship_acceleration', 0.3, 'Ship acceleration factor')
            self.add_setting('Ship', 'ship_hit_points', 4, 'Number of hits ship takes before it is destroyed')
            self.add_setting('Ship', 'ship_max_vel', 6, "Ship's maximum velocity")
            self.add_setting('Ship', 'ship_orientation', 90, 'Initial ship orientation')
            self.add_setting('Ship', 'ship_pos_x', 245, 'Initial ship x position')
            self.add_setting('Ship', 'ship_pos_y', 315, 'Initial ship y position')
            self.add_setting('Ship', 'ship_radius', 3, 'ship collision radius.')
            self.add_setting('Ship', 'ship_turn_speed', 6, "Ship's turning speed")
            self.add_setting('Ship', 'ship_vel_x', 0, 'Initial ship velocity in x direction')
            self.add_setting('Ship', 'ship_vel_y', 0, 'Initial ship velocity in y direction.')
            
            self.add_setting('Missle', 'missile_max', 100, 'Maximum number of missiles possible')
            self.add_setting('Missle', 'missile_num', 100, 'Number of missiles at start of game')
            self.add_setting('Missle', 'missile_penalty', 3, 'Points lost when you fire a missile when none remain')
            self.add_setting('Missle', 'missile_radius', 5, 'Missile collision radius')
            self.add_setting('Missle', 'missile_speed', 20, 'Speed of missile fired from ship')
            
            self.add_setting('Hexagon', 'hex_pos_x', 355, 'Hex x position')
            self.add_setting('Hexagon', 'hex_pos_y', 315, 'Hex y position')
            self.add_setting('Hexagon', 'big_hex', 200, '"Radius" of large hexagon')
            self.add_setting('Hexagon', 'small_hex', 40, '"Radius" of small hexagon')
            self.add_setting('Hexagon', 'hex_shrink', False, type=CT_CHECKBOX, about='Does the outer hex shrink over time?')
            self.add_setting('Hexagon', 'hex_shrink_radius', 150, 'If hex shrinks, to what minimum radius?')
            
            self.add_setting('Fortress', 'fortress_exists', True, type=CT_CHECKBOX, about='Does the fortress exist?')
            self.add_setting('Fortress', 'fortress_lock_time', 1000, 'Time in milliseconds it takes the fortress to lock on to the ship before firing')
            self.add_setting('Fortress', 'fortress_pos_x', 355, 'Fortress x position')
            self.add_setting('Fortress', 'fortress_pos_y', 315, 'Fortress y position')
            self.add_setting('Fortress', 'fortress_radius', 18, 'Fortress collision radius')
            self.add_setting('Fortress', 'fortress_sector_size', 10, 'Fortress "sector size." Angle of tolerance before fortress turns to face ship. Bigger means fortress fires more often')
            self.add_setting('Fortress', 'hit_fortress_while_mine', False, type=CT_CHECKBOX, about="Can the fortress be hit if there's a mine onscreen?")
            self.add_setting('Fortress', 'vlner_threshold', 10, 'Minimum vulnerability before you can destroy the fortress with a double shot. Note - keep in mind that the first shot of a "double shot" will increase VLNER')
            self.add_setting('Fortress', 'vlner_time', 250, 'Time in milliseconds that must pass between shots to avoid the fortress vulnerability to reset')
    
            self.add_setting('Shell', 'shell_speed', 6, 'Speed of shell fired from fortress')
            self.add_setting('Shell', 'shell_radius', 3, 'Shell collision radius')
            
            self.add_setting('Bonus', 'bonus_exists', True, type=CT_CHECKBOX, about='Do bonuses exist?')
            self.add_setting('Bonus', 'bonus_system', "AX-CPT", type=CT_LINEEDIT, about='Bonus system standard or AX-CPT?')
            self.add_setting('Bonus', 'randomize_bonus_pos', False, type=CT_CHECKBOX, about='Randomize bonus position?')
            self.add_setting('Bonus', 'bonus_pos_x', 355, 'Bonus x position')
            self.add_setting('Bonus', 'bonus_pos_y', 390, 'Bonus y position')
            self.add_setting('Bonus', 'bonus_probability', 0.3, 'Probability that next symbol will be the bonus symbol')
            self.add_setting('Bonus', 'bonus_symbol', '$', type=CT_LINEEDIT, about='Bonus symbol')
            self.add_setting('Bonus', 'non_bonus_symbols', ['!', '&', '*', '%', '@'], type=CT_LINEEDIT, about="Non-bonus symbols. Defaults are # & * % @. Don't use '-', because that's used in the log file to represent that there's no symbol present")
            self.add_setting('Bonus', 'symbol_down_time', 833, '"Blank time" between symbol appearances in milliseconds**. (Seems like a weird number, but it\'s to sync with the frame-based original)')
            self.add_setting('Bonus', 'symbol_up_time', 2500, 'Time in milliseconds each symbol is visible**')
    
            self.add_setting('Mine', 'mine_exists', True, type=CT_CHECKBOX, about='Do mines exists?')
            self.add_setting('Mine', 'mine_mode', 'standard', type=CT_LINEEDIT, about='Set mine behavior to standard or MOT')
            self.add_setting('Mine', 'num_foes', 3, 'Number of foe mines')
            self.add_setting('Mine', 'mine_radius', 20, 'Mine collision radius')
            self.add_setting('Mine', 'mine_speed', 3, 'Mine speed')
            self.add_setting('Mine', 'minimum_spawn_distance', 200, 'Minimum spawn distance. Mine will never appear closer than this distance to the ship')
            self.add_setting('Mine', 'maximum_spawn_distance', 700, 'Maximum spawn distance. Mine will never appear farther away than this distance to the ship')
            self.add_setting('Mine', 'intrvl_min', 250, 'Minimum time between double-clicks to identify foe mine')
            self.add_setting('Mine', 'intrvl_max', 400, 'Maximum time between double-clicks to identify foe mine')
            self.add_setting('Mine', 'mine_probability', 0.3, 'Probability that next mine will be a foe')
            self.add_setting('Mine', 'mine_timeout', 10000, 'Time in milliseconds for a mine to timeout and disappear')
            self.add_setting('Mine', 'mine_spawn', 5000, 'Time in milliseconds for a mine to spawn')
            self.add_setting('Mine', 'fortress_resets_mine', True, type=CT_CHECKBOX, about='Does destroying the fortress reset the mine timer?')
            
            self.add_setting('MOT', 'MOT_count', 5, 'Number of mines')
            self.add_setting('MOT', 'MOT_identification_time', 5000, 'Time to allow for MOT identification')
            self.add_setting('MOT', 'MOT_identification_type', 'shots', type=CT_LINEEDIT, about='MOT identification through shots or ship? (i.e., fly into the mine)')
            self.add_setting('MOT', 'MOT_max_deflection', 15, 'Angle in degrees for the maximum amount a mine can change direction')
            self.add_setting('MOT', 'MOT_move_time', 5000, 'Time to move mines with IFF info hidden')
            self.add_setting('MOT', 'MOT_movement_style', 'bounce', type=CT_LINEEDIT, about='Do MOT mines bounce off walls or warp around edges?')
            self.add_setting('MOT', 'MOT_off_time', 5000, 'Time in between MOT "cycles"')
            self.add_setting('MOT', 'MOT_onset_time', 3000, 'Time to display "frozen" MOT mines on onset')
            self.add_setting('MOT', 'MOT_switch_time', 1000, 'Time in between direction changes while MOT mines are moving')
    
            self.add_setting('Score', 'new_scoring', False, type=CT_CHECKBOX, about='Use the new scoring system for Flight, Fortress, and Mines? (instead of PNTS, CNTRL, VLCTY and SPEED)')
            self.add_setting('Score', 'new_scoring_pos', True, type=CT_CHECKBOX, about='New scoring position is a more "eye-tracker friendly" format that places the scores around the perimeter of the gameworld, rather than just all along the bottom. Set to f for default positioning')
            self.add_setting('Score', 'PNTS_pos', 1, 'Set positions for the display elements. 1 = leftmost for original scoring position for new scoring position, 1 = left item on top row, proceeds clockwise PNTS position(or Flight, for new)')
            self.add_setting('Score', 'CNTRL_pos', 2, 'CNTRL position(or Fortress, for new)')
            self.add_setting('Score', 'VLCTY_pos', 3, 'VLCTY position(or Mines, for new)')
            self.add_setting('Score', 'VLNER_pos', 4, 'VLNER position')
            self.add_setting('Score', 'IFF_pos', 5, 'IFF')
            self.add_setting('Score', 'INTRVL_pos', 6, 'INTRVL')
            self.add_setting('Score', 'SPEED_pos', 7, 'SPEED position(or Bonus, for new)')
            self.add_setting('Score', 'SHOTS_pos', 8, 'SHOTS')
            self.add_setting('Score', 'update_timer', 1000, 'How often (in milliseconds) the VLCTY and CNTRL scores update (or Flight, for new)')
            self.add_setting('Score', 'speed_threshold', 4, 'Speed at which you\'re considered to be going "too fast", resulting in a VLCTY point penalty (or Flight, for new)')
            self.add_setting('Score', 'VLCTY_increment', 7, 'VLCTY bonus/penalty for going either slow enough or too fast (or Flight, for new)')
            self.add_setting('Score', 'CNTRL_increment', 6, 'Number of points added to CNTRL score for staying with the hexagons (or Flight, For new). Note that half this number is added when outside the hexagons, so even is recommended.')
            self.add_setting('Score', 'small_hex_penalty', 5, 'Penalty for colliding with the small hexagon.')
            self.add_setting('Score', 'warp_penalty', 35, 'Penalty for warping around the screen')
            self.add_setting('Score', 'mine_timeout_penalty', 50, 'Penalty for mine timing out')
            self.add_setting('Score', 'mine_hit_penalty', 50, 'Penalty for mine hitting ship')
            self.add_setting('Score', 'shell_hit_penalty', 50, 'Penalty for shell hitting ship')
            self.add_setting('Score', 'ship_death_penalty', 100, 'Penalty for ship destruction')
            self.add_setting('Score', 'energize_friend', 20, 'Points for "energizing" a friendly mine')
            self.add_setting('Score', 'destroy_foe', 30, 'Points for destroying a "foe" mine.')
            self.add_setting('Score', 'destroy_fortress', 100, 'Points for destroying the fortress')
            self.add_setting('Score', 'bonus_points', 100, 'Points added for selecting points bonus')
            self.add_setting('Score', 'bonus_missiles', 50, 'Missiles added for selecting missile bonus')
    
        if load:
            
            config_file = os.path.join(get_config_home(),'config')
            if os.path.isfile(config_file):
                with open(config_file, 'r') as f:
                    s = f.read()
                    if s:
                        config = json.loads(s)
                        for c in config.keys():
                            for s in config[c].keys():
                                self.update_setting_value(c,s,config[c][s]['value'])
                            
def diff_config(config):
    defC=Config(load=False)
    newC = Config(defaults=False, load=False)
    config_file = os.path.join(get_config_home(),'config')
    for c in config.keys():
        for s in config[c].keys():
            if config[c][s]['value'] != defC.config[c][s]['value']:
                newC.add_setting(c, s, config[c][s]['value'])
    return newC.config
                
def save_config(config):
    with open(config_file, 'w+') as f:
        json.dump(config, f, separators=(',',': '), indent=4, sort_keys=True)

def gen_config():
    config = Config()
    save_config(config.config)
    
class ConfigEditor(QMainWindow):
    
    def __init__(self):
        super(ConfigEditor, self).__init__()
        
        self.config = Config()
        
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
                    w = QLineEdit()
                    w.setText(str(info['value']))
                    if info.has_key('n'):
                        w.setMaxLength(info['n'])
                        w.setFixedWidth(info['n']*w.minimumSizeHint().height())
                elif info['type'] == CT_CHECKBOX:
                    w = QCheckBox()
                    if info['value']:
                        w.setCheckState(Qt.Checked)
                    else:
                        w.setCheckState(Qt.Unchecked)
                elif info['type'] == CT_SPINBOX:
                    w = QSpinBox()
                    w.setMaximum(1000000)
                    w.setValue(info['value'])
                elif info['type'] == CT_COMBO:
                    w = QComboBox()
                    if info.has_key('options'):
                        w.addItems(info['options'])
                        for i in range(0,len(info['options'])):
                            if info['options'][i] == info['value']:
                                w.setCurrentIndex(i)
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
        self.setWindowTitle('Spacefortress Config Editor')
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
        config = diff_config(self.config.config)
        if config:
            print 'settings have changed'
            save_config(config)
        self.quitApp()
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = ConfigEditor()
    sys.exit(app.exec_())
    
