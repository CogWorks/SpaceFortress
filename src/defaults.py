import sys, os, platform
from jsonConfig.config import Config
from jsonConfig.constants import *

logDrivers = [ 'Default' ]

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

def get_plugin_home():
    return os.path.join(get_config_home(), 'Plugins')

def get_user_file():
    return os.path.join(get_config_home(), 'config')

def load_plugins(app, dir, plugins):
    dir = os.path.abspath(dir)
    sys.path.append(dir)
    if os.path.exists(dir):
        for f in os.listdir(dir):
            module_name, ext = os.path.splitext(f)
            if ext == '.py':
                module = __import__(module_name)
                if not plugins.has_key(module_name):
                    try:
                        plugins[module_name] = module.SF5Plugin(app)
                        if hasattr(plugins[module_name], 'logDrivers'):
                            for d in plugins[module_name].logDrivers:
                                logDrivers.append(module_name + ':' + d)
                    except AttributeError:
                        pass
    return plugins

def validate_string_len(info):
    if len(info['value']) == info['n']:
        return True
    else:
        return False

def validate_flight_bias(info):
    if -1 <= info['value'] <= 1:
        return True
    else:
        return False

def validate_quadrant_probs(info):
    try:
        list = info['value'].split(',')
        if len(list) == 4 and sum(map(float, list)) == 1.0:
            return True
        else:
            return False
    except ValueError:
        return False

def get_config():

    cfg = Config()

    cfg.add_setting('General', 'next_gen', True, type=2, alias='Next Gen Mode')
    cfg.add_setting('General', 'id', '1234', alias='Subject ID#', type=CT_LINEEDIT, about='Subject identifier used in log filename"')
    cfg.add_setting('General', 'games_per_session', 8, alias='Max # of Games', about='Number of games per "session"')
    cfg.add_setting('General', 'bonus_system', "AX-CPT", alias="Bonus System", type=CT_COMBO, options=['standard', 'AX-CPT'], about='Bonus system standard or AX-CPT?')
    cfg.add_setting('General', 'bonus_location', 'Random', alias='Bonus Location', type=CT_COMBO, options=['Fixed', 'Random', 'Probabilistic'], about='Randomize bonus position?')
    cfg.add_setting('General', 'game_time', 300000, alias='Game Duration (ms)', about='Time in milliseconds for a game. NOTE! If you escape in the middle of a game, the log will have "short" prepended to the name')
    cfg.add_setting('General', 'sound', True, alias='Sound', type=CT_CHECKBOX, about='Enable/disable sound')
    cfg.add_setting('General', 'allow_pause', True, alias='Allow Pausing', type=CT_CHECKBOX, about='Enable/disable whether or not pausing is allowed.')

    cfg.add_setting('Display', 'display_mode', 'Fullscreen', alias='Display Mode', options=['Fullscreen', 'Current', 'Windowed', 'Fake Fullscreen'], type=CT_COMBO, about='Run at full screen? Set to f to run in a window')
    cfg.add_setting('Display', 'linewidth', 1, alias='Linewidth', about='Width of lines drawn on screen. Increase for a more "projector-friendly" game')
    cfg.add_setting('Display', 'screen_width', 0, alias='Screen Width', type=CT_SPINBOX)
    cfg.add_setting('Display', 'screen_height', 0, alias='Screen Height', type=CT_SPINBOX)
    cfg.add_setting('Display', 'pause_overlay', True, alias='Pause Overlay', type=CT_CHECKBOX, about='Blank screen and show "Paused!" when game is paused.')
    cfg.add_setting('Display', 'show_fps', False, type=CT_CHECKBOX)
    cfg.add_setting('Display', 'show_et', False, type=CT_CHECKBOX)
    cfg.add_setting('Display', 'show_kp', False, type=CT_CHECKBOX)

    cfg.add_setting('Graphics', 'show_starfield', True, type=2)
    cfg.add_setting('Graphics', 'max_stars', 250)
    cfg.add_setting('Graphics', 'star_speed', .5, type=CT_DBLSPINBOX)
    cfg.add_setting('Graphics', 'fancy', True, type=CT_CHECKBOX)
    cfg.add_setting('Graphics', 'parallax_mode', 'Random', type=CT_COMBO, options=['Random', 'Fortress'])

    cfg.add_setting('Logging', 'logging', True, alias='Logging', type=CT_CHECKBOX, about='Enable/disable logging')
    cfg.add_setting('Logging', 'logdir', '', alias='Log Directory', type=CT_LINEEDIT, about='Directory for log files, leave blank for default.')
    cfg.add_setting('Logging', 'logDriver', 'Default', alias='Log Driver', type=CT_COMBO, options=logDrivers)

    cfg.add_setting('Keybindings', 'fire_key', 'SPACE', alias='Fire', type=CT_COMBO, options=PYGAME_KEYS)
    cfg.add_setting('Keybindings', 'thrust_key', 'w', alias='Thrust', type=CT_COMBO, options=PYGAME_KEYS)
    cfg.add_setting('Keybindings', 'left_turn_key', 'a', alias='Turn Left', type=CT_COMBO, options=PYGAME_KEYS)
    cfg.add_setting('Keybindings', 'right_turn_key', 'd', alias='Turn Right', type=CT_COMBO, options=PYGAME_KEYS)
    cfg.add_setting('Keybindings', 'shots_key', 'k', alias='Shots Bonus', type=CT_COMBO, options=PYGAME_KEYS)
    cfg.add_setting('Keybindings', 'pnts_key', 'l', alias='Points Bonus', type=CT_COMBO, options=PYGAME_KEYS)
    cfg.add_setting('Keybindings', 'IFF_key', 'j', alias='Identify Friend or Foe', type=CT_COMBO, options=PYGAME_KEYS)
    cfg.add_setting('Keybindings', 'pause_key', 'p', alias='Pause', type=CT_COMBO, options=PYGAME_KEYS)

    cfg.add_setting('Ship', 'ship_acceleration', 0.3, 'Ship acceleration factor', type=CT_DBLSPINBOX)
    cfg.add_setting('Ship', 'ship_hit_points', 4, 'Number of hits ship takes before it is destroyed')
    cfg.add_setting('Ship', 'ship_max_vel', 6, "Ship's maximum velocity")
    cfg.add_setting('Ship', 'ship_orientation', 90, 'Initial ship orientation')
    cfg.add_setting('Ship', 'ship_pos_x', 245, 'Initial ship x position')
    cfg.add_setting('Ship', 'ship_pos_y', 315, 'Initial ship y position')
    cfg.add_setting('Ship', 'ship_radius', 12, 'ship collision radius.')
    cfg.add_setting('Ship', 'ship_turn_speed', 6, "Ship's turning speed")
    cfg.add_setting('Ship', 'ship_vel_x', 0, 'Initial ship velocity in x direction')
    cfg.add_setting('Ship', 'ship_vel_y', 0, 'Initial ship velocity in y direction.')
    cfg.add_setting('Ship', 'colored_damage', True, type=CT_CHECKBOX)

    cfg.add_setting('Missile', 'missile_max', 50, 'Maximum number of missiles possible')
    cfg.add_setting('Missile', 'missile_num', 50, 'Number of missiles at start of game')
    cfg.add_setting('Missile', 'missile_penalty', 3, 'Points lost when you fire a missile when none remain')
    cfg.add_setting('Missile', 'missile_radius', 5, 'Missile collision radius')
    cfg.add_setting('Missile', 'missile_speed', 20, 'Speed of missile fired from ship')
    cfg.add_setting('Missile', 'empty_penalty', True, type=2, alias='Fire when empty penalty')

    cfg.add_setting('Hexagon', 'hex_pos_x', 355, 'Hex x position')
    cfg.add_setting('Hexagon', 'hex_pos_y', 315, 'Hex y position')
    cfg.add_setting('Hexagon', 'big_hex', 200, '"Radius" of large hexagon')
    cfg.add_setting('Hexagon', 'small_hex', 40, '"Radius" of small hexagon')
    cfg.add_setting('Hexagon', 'hex_shrink', False, type=CT_CHECKBOX, about='Does the outer hex shrink over time?')
    cfg.add_setting('Hexagon', 'hex_shrink_radius', 150, 'If hex shrinks, to what minimum radius?')
    cfg.add_setting('Hexagon', 'hide_big_hex', True, type=CT_CHECKBOX)
    cfg.add_setting('Hexagon', 'hide_small_hex', True, type=CT_CHECKBOX)

    cfg.add_setting('Fortress', 'fortress_exists', True, type=CT_CHECKBOX, about='Does the fortress exist?')
    cfg.add_setting('Fortress', 'fortress_lock_time', 800, 'Time in milliseconds it takes the fortress to lock on to the ship before firing')
    cfg.add_setting('Fortress', 'fortress_pos_x', 355, 'Fortress x position')
    cfg.add_setting('Fortress', 'fortress_pos_y', 315, 'Fortress y position')
    cfg.add_setting('Fortress', 'fortress_radius', 18, 'Fortress collision radius')
    cfg.add_setting('Fortress', 'fortress_sector_size', 20, 'Fortress "sector size." Angle of tolerance before fortress turns to face ship. Bigger means fortress fires more often')
    cfg.add_setting('Fortress', 'hit_fortress_while_mine', False, type=CT_CHECKBOX, about="Can the fortress be hit if there's a mine onscreen?")
    cfg.add_setting('Fortress', 'vlner_threshold', 10, 'Minimum vulnerability before you can destroy the fortress with a double shot. Note - keep in mind that the first shot of a "double shot" will increase VLNER')
    cfg.add_setting('Fortress', 'vlner_time', 250, 'Time in milliseconds that must pass between shots to avoid the fortress vulnerability to reset')

    cfg.add_setting('Shell', 'shell_speed', 6, 'Speed of shell fired from fortress')
    cfg.add_setting('Shell', 'shell_radius', 3, 'Shell collision radius')

    cfg.add_setting('Bonus', 'bonus_exists', True, type=CT_CHECKBOX, about='Do bonuses exist?')
    cfg.add_setting('Bonus', 'bonus_pos_x', 355, 'Bonus x position')
    cfg.add_setting('Bonus', 'bonus_pos_y', 390, 'Bonus y position')
    cfg.add_setting('Bonus', 'bonus_probability', 0.3, 'Probability that next symbol will be the bonus symbol')
    cfg.add_setting('Bonus', 'bonus_symbol', '$', type=CT_LINEEDIT, n=1, validate=validate_string_len, about='Bonus symbol')
    cfg.add_setting('Bonus', 'non_bonus_symbols', '!&*%@', type=CT_LINEEDIT, about="Non-bonus symbols. Defaults are # & * % @. Don't use '-', because that's used in the log file to represent that there's no symbol present")
    cfg.add_setting('Bonus', 'symbol_down_time', 833, '"Blank time" between symbol appearances in milliseconds**. (Seems like a weird number, but it\'s to sync with the frame-based original)')
    cfg.add_setting('Bonus', 'symbol_up_time', 2500, 'Time in milliseconds each symbol is visible**')
    cfg.add_setting('Bonus', 'quadrant_probs', '.2,.2,.2,.4', type=CT_LINEEDIT, validate=validate_quadrant_probs)

    cfg.add_setting('AX-CPT', 'cue_visibility', 1250, 'The time cue is visible in ms')
    cfg.add_setting('AX-CPT', 'target_visibility', 1250, 'The time cue is visible in ms')
    cfg.add_setting('AX-CPT', 'isi_time', 800, 'time between cue and target (variable)')
    cfg.add_setting('AX-CPT', 'iti_time', 800, 'time between target and cue')
    cfg.add_setting('AX-CPT', 'ax_prob', .4, type=CT_DBLSPINBOX, about="probability that next pair will be correct cue followed by correct target")
    cfg.add_setting('AX-CPT', 'ay_prob', .2, type=CT_DBLSPINBOX)
    cfg.add_setting('AX-CPT', 'bx_prob', .2, type=CT_DBLSPINBOX)
    cfg.add_setting('AX-CPT', 'by_prob', .2, type=CT_DBLSPINBOX)
    cfg.add_setting('AX-CPT', 'a_symbols', "#", type=CT_LINEEDIT, about="symbols to draw for correct cues")
    cfg.add_setting('AX-CPT', 'b_symbols', "@", type=CT_LINEEDIT)
    cfg.add_setting('AX-CPT', 'x_symbols', "$", type=CT_LINEEDIT)
    cfg.add_setting('AX-CPT', 'y_symbols', "&", type=CT_LINEEDIT)
    cfg.add_setting('AX-CPT', 'state', 'iti', type=CT_COMBO, options=['iti', 'isi', 'cue', 'target'], alias="State")

    cfg.add_setting('Mine', 'mine_exists', True, type=CT_CHECKBOX, about='Do mines exists?')
    cfg.add_setting('Mine', 'mine_mode', 'standard', type=CT_COMBO, options=['standard'], about='Set mine behavior to standard or MOT')
    cfg.add_setting('Mine', 'num_foes', 3, 'Number of foe mines')
    cfg.add_setting('Mine', 'mine_radius', 20, 'Mine collision radius')
    cfg.add_setting('Mine', 'mine_speed', 3, 'Mine speed')
    cfg.add_setting('Mine', 'minimum_spawn_distance', 200, 'Minimum spawn distance. Mine will never appear closer than this distance to the ship')
    cfg.add_setting('Mine', 'maximum_spawn_distance', 700, 'Maximum spawn distance. Mine will never appear farther away than this distance to the ship')
    cfg.add_setting('Mine', 'intrvl_min', 250, 'Minimum time between double-clicks to identify foe mine')
    cfg.add_setting('Mine', 'intrvl_max', 400, 'Maximum time between double-clicks to identify foe mine')
    cfg.add_setting('Mine', 'mine_probability', 0.3, 'Probability that next mine will be a foe', type=CT_DBLSPINBOX)
    cfg.add_setting('Mine', 'mine_timeout', 10000, 'Time in milliseconds for a mine to timeout and disappear')
    cfg.add_setting('Mine', 'mine_spawn', 5000, 'Time in milliseconds for a mine to spawn')
    cfg.add_setting('Mine', 'fortress_resets_mine', False, type=CT_CHECKBOX, about='Does destroying the fortress reset the mine timer?')

    cfg.add_setting('MOT', 'MOT_count', 5, 'Number of mines')
    cfg.add_setting('MOT', 'MOT_identification_time', 5000, 'Time to allow for MOT identification')
    cfg.add_setting('MOT', 'MOT_identification_type', 'shots', type=CT_LINEEDIT, about='MOT identification through shots or ship? (i.e., fly into the mine)')
    cfg.add_setting('MOT', 'MOT_max_deflection', 15, 'Angle in degrees for the maximum amount a mine can change direction')
    cfg.add_setting('MOT', 'MOT_move_time', 5000, 'Time to move mines with IFF info hidden')
    cfg.add_setting('MOT', 'MOT_movement_style', 'bounce', type=CT_LINEEDIT, about='Do MOT mines bounce off walls or warp around edges?')
    cfg.add_setting('MOT', 'MOT_off_time', 5000, 'Time in between MOT "cycles"')
    cfg.add_setting('MOT', 'MOT_onset_time', 3000, 'Time to display "frozen" MOT mines on onset')
    cfg.add_setting('MOT', 'MOT_switch_time', 1000, 'Time in between direction changes while MOT mines are moving')

    cfg.add_setting('Score', 'new_scoring', True, type=CT_CHECKBOX, about='Use the new scoring system for Flight, Fortress, and Mines? (instead of PNTS, CNTRL, VLCTY and SPEED)')
    cfg.add_setting('Score', 'new_scoring_pos', True, type=CT_CHECKBOX, about='New scoring position is a more "eye-tracker friendly" format that places the scores around the perimeter of the gameworld, rather than just all along the bottom. Set to f for default positioning')
    #Set positions for the display elements. 1 = leftmost for original scoring position for new scoring position, 1 = left item on top row, proceeds clockwise
    cfg.add_setting('Score', 'PNTS_pos', 1, ' PNTS position(or Flight, for new)')
    cfg.add_setting('Score', 'CNTRL_pos', 2, 'CNTRL position(or Fortress, for new)')
    cfg.add_setting('Score', 'VLCTY_pos', 6, 'VLCTY position(or Mines, for new)')
    cfg.add_setting('Score', 'VLNER_pos', 3, 'VLNER position')
    cfg.add_setting('Score', 'IFF_pos', 7, 'IFF')
    cfg.add_setting('Score', 'INTRVL_pos', 4, 'INTRVL')
    cfg.add_setting('Score', 'SPEED_pos', 5, 'SPEED position(or Bonus, for new)')
    cfg.add_setting('Score', 'SHOTS_pos', 8, 'SHOTS')
    cfg.add_setting('Score', 'flight_bias', 0, type=CT_DBLSPINBOX, validate=validate_flight_bias)
    cfg.add_setting('Score', 'flight_max_increment', 20, 'The max flight score increment')
    cfg.add_setting('Score', 'update_timer', 1000, 'How often (in milliseconds) the VLCTY and CNTRL scores update (or Flight, for new)')
    cfg.add_setting('Score', 'speed_threshold', 4, 'Speed at which you\'re considered to be going "too fast", resulting in a VLCTY point penalty (or Flight, for new)')
    cfg.add_setting('Score', 'VLCTY_increment', 7, 'VLCTY bonus/penalty for going either slow enough or too fast (or Flight, for new)')
    cfg.add_setting('Score', 'CNTRL_increment', 6, 'Number of points added to CNTRL score for staying with the hexagons (or Flight, For new). Note that half this number is added when outside the hexagons, so even is recommended.')
    cfg.add_setting('Score', 'small_hex_penalty', 5, 'Penalty for colliding with the small hexagon.')
    cfg.add_setting('Score', 'warp_penalty', 35, 'Penalty for warping around the screen')
    cfg.add_setting('Score', 'mine_timeout_penalty', 50, 'Penalty for mine timing out')
    cfg.add_setting('Score', 'mine_hit_penalty', 50, 'Penalty for mine hitting ship')
    cfg.add_setting('Score', 'shell_hit_penalty', 50, 'Penalty for shell hitting ship')
    cfg.add_setting('Score', 'ship_death_penalty', 100, 'Penalty for ship destruction')
    cfg.add_setting('Score', 'energize_friend', 20, 'Points for "energizing" a friendly mine')
    cfg.add_setting('Score', 'destroy_foe', 30, 'Points for destroying a "foe" mine.')
    cfg.add_setting('Score', 'destroy_fortress', 250, 'Points for destroying the fortress')
    cfg.add_setting('Score', 'bonus_points', 100, 'Points added for selecting points bonus')
    cfg.add_setting('Score', 'bonus_missiles', 50, 'Missiles added for selecting missile bonus')

    cfg.add_setting('Joystick', 'use_joystick', False, type=CT_CHECKBOX)
    cfg.add_setting('Joystick', 'joystick_id', 0)
    cfg.add_setting('Joystick', 'invert_x', False, type=CT_CHECKBOX)
    cfg.add_setting('Joystick', 'invert_y', True, type=CT_CHECKBOX)
    cfg.add_setting('Joystick', 'fire_button', 0)
    cfg.add_setting('Joystick', 'iff_button', 3)
    cfg.add_setting('Joystick', 'shots_button', 1)
    cfg.add_setting('Joystick', 'pnts_button', 2)

    cfg.add_setting('Playback', 'playback', False, type=2)
    cfg.add_setting('Playback', 'makevideo', False, type=2)

    return cfg
