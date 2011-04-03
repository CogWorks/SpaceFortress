import json, copy

class Config():
    
    config = {}
    
    def add_category(self, category):
        if not self.config.has_key(category):
            self.config[category] = {}
            
    def add_setting(self, category, setting, value, about=''):
        assert category!=None, 'Must specify a category'
        assert setting!=None, 'Must specify a setting'
        assert value!=None, 'Must specify a value'
        self.add_category(category)
        if not self.config[category].has_key(setting):
            self.config[category][setting] = {}
        self.config[category][setting]['value'] = value
        self.config[category][setting]['about'] = about
        
    def get_setting(self, category, setting):
        assert category!=None, 'Must specify a category'
        assert setting!=None, 'Must specify a setting'
        assert self.config.has_key(category), 'Category does not exist'
        assert self.config[category].has_key(setting), 'Setting in category does not exist'
        assert self.config[category][setting].has_key('value'), 'Setting in category has no value'
        return self.config[category][setting]['value']
        
    def __init__(self):
        
        self.add_setting('General', 'human', True, 'Will this game be played by a human or a cognitive model? Set to f to disable human control, enabling ACT-R')
        self.add_setting('General', 'fullscreen', False, 'Run at full screen? Set to f to run in a window')
        self.add_setting('General', 'linewidth', 1, 'Width of lines drawn on screen. Increase for a more "projector-friendly" game')
        self.add_setting('General', 'psf', False, 'Original PSF (SF4) settings? If t, *ALL* further values are ignored')
        self.add_setting('General', 'game_time', 30000, 'Time in milliseconds for a game. NOTE! If you escape in the middle of a game, the log will have "short" prepended to the name')
        self.add_setting('General', 'games_per_session', 8, 'Number of games per "session"')
        self.add_setting('General', 'print_events', False, 'Print events to stdout')
        self.add_setting('General', 'sound', True, 'Enable/disable sound')
        
        self.add_setting('Keybindings', 'thrust_key', 'w')
        self.add_setting('Keybindings', 'left_turn_key', 'a')
        self.add_setting('Keybindings', 'right_turn_key', 'd')
        self.add_setting('Keybindings', 'fire_key', 'SPACE')
        self.add_setting('Keybindings', 'IFF_key', 'j')
        self.add_setting('Keybindings', 'shots_key', 'k')
        self.add_setting('Keybindings', 'pnts_key', 'l')
        
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
        self.add_setting('Hexagon', 'hex_shrink', False, 'Does the outer hex shrink over time?')
        self.add_setting('Hexagon', 'hex_shrink_radius', 150, 'If hex shrinks, to what minimum radius?')
        
        self.add_setting('Fortress', 'fortress_exists', True, 'Does the fortress exist?')
        self.add_setting('Fortress', 'fortress_lock_time', 1000, 'Time in milliseconds it takes the fortress to lock on to the ship before firing')
        self.add_setting('Fortress', 'fortress_pos_x', 355, 'Fortress x position')
        self.add_setting('Fortress', 'fortress_pos_y', 315, 'Fortress y position')
        self.add_setting('Fortress', 'fortress_radius', 18, 'Fortress collision radius')
        self.add_setting('Fortress', 'fortress_sector_size', 10, 'Fortress "sector size." Angle of tolerance before fortress turns to face ship. Bigger means fortress fires more often')
        self.add_setting('Fortress', 'hit_fortress_while_mine', False, "Can the fortress be hit if there's a mine onscreen?")
        self.add_setting('Fortress', 'vlner_threshold', 10, 'Minimum vulnerability before you can destroy the fortress with a double shot. Note - keep in mind that the first shot of a "double shot" will increase VLNER')
        self.add_setting('Fortress', 'vlner_time', 250, 'Time in milliseconds that must pass between shots to avoid the fortress vulnerability to reset')

        self.add_setting('Shell', 'shell_speed', 6, 'Speed of shell fired from fortress')
        self.add_setting('Shell', 'shell_radius', 3, 'Shell collision radius')
        
        self.add_setting('Bonus', 'bonus_exists', True, 'Do bonuses exist?')
        self.add_setting('Bonus', 'bonus_system', "AX-CPT", 'Bonus system standard or AX-CPT?')
        self.add_setting('Bonus', 'randomize_bonus_pos', False, 'Randomize bonus position?')
        self.add_setting('Bonus', 'bonus_pos_x', 355, 'Bonus x position')
        self.add_setting('Bonus', 'bonus_pos_y', 390, 'Bonus y position')
        self.add_setting('Bonus', 'bonus_probability', 0.3, 'Probability that next symbol will be the bonus symbol')
        self.add_setting('Bonus', 'bonus_symbol', '$', 'Bonus symbol')
        self.add_setting('Bonus', 'non_bonus_symbols', ['!', '&', '*', '%', '@'], "Non-bonus symbols. Defaults are # & * % @. Don't use '-', because that's used in the log file to represent that there's no symbol present")
        self.add_setting('Bonus', 'symbol_down_time', 833, '"Blank time" between symbol appearances in milliseconds**. (Seems like a weird number, but it\'s to sync with the frame-based original)')
        self.add_setting('Bonus', 'symbol_up_time', 2500, 'Time in milliseconds each symbol is visible**')

        self.add_setting('Mine', 'mine_exists', True, 'Do mines exists?')
        self.add_setting('Mine', 'mine_mode', 'standard', 'Set mine behavior to standard or MOT')
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
        self.add_setting('Mine', 'fortress_resets_mine', True, 'Does destroying the fortress reset the mine timer?')
        
        self.add_setting('MOT', 'MOT_count', 5, 'Number of mines')
        self.add_setting('MOT', 'MOT_identification_time', 5000, 'Time to allow for MOT identification')
        self.add_setting('MOT', 'MOT_identification_type', 'shots', 'MOT identification through shots or ship? (i.e., fly into the mine)')
        self.add_setting('MOT', 'MOT_max_deflection', 15, 'Angle in degrees for the maximum amount a mine can change direction')
        self.add_setting('MOT', 'MOT_move_time', 5000, 'Time to move mines with IFF info hidden')
        self.add_setting('MOT', 'MOT_movement_style', 'bounce', 'Do MOT mines bounce off walls or warp around edges?')
        self.add_setting('MOT', 'MOT_off_time', 5000, 'Time in between MOT "cycles"')
        self.add_setting('MOT', 'MOT_onset_time', 3000, 'Time to display "frozen" MOT mines on onset')
        self.add_setting('MOT', 'MOT_switch_time', 1000, 'Time in between direction changes while MOT mines are moving')

        self.add_setting('Score', 'new_scoring', False, 'Use the new scoring system for Flight, Fortress, and Mines? (instead of PNTS, CNTRL, VLCTY and SPEED)')
        self.add_setting('Score', 'new_scoring_pos', True, 'New scoring position is a more "eye-tracker friendly" format that places the scores around the perimeter of the gameworld, rather than just all along the bottom. Set to f for default positioning')
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
        
def load_config(config_file):
    config = get_default_config()
    try:
        with open(config_file, 'r') as f:
            config.update(json.load(f))
    except IOError:
        pass
    return config

def gen_config(config_file):
    ret = True
    config = Config().config
    try:
        with open(config_file, 'w+') as f:
            json.dump(config, f, separators=(',',': '), indent=4, sort_keys=True)
    except IOError:
        ret = False
    return ret

if __name__ == '__main__':
    
    config = Config()
    print config.config
    gen_config("/tmp/config")