import json, copy

def get_default_config():
    return {
        
        ### GENERAL SETTINGS ###
        
        #Will this game be played by a human or a cognitive model?
        #Set to f to disable human control, enabling ACT-R
        'human': True,     
        #Run at full screen? Set to f to run in a window
        'fullscreen': False,
        #Width of lines drawn on screen. Increase for a more "projector-friendly" game
        'linewidth': 1,
        #Original PSF (SF4) settings? If t, *ALL* further values are ignored
        'psf': False,
        #Time in milliseconds for a game.
        #NOTE! If you escape in the middle of a game, the log will have
        #"short" prepended to the name
        'game_time': 30000,
        #Number of games per "session."
        'games_per_session': 8,
        #Key bindings - use digits, lowercase letters, or caps for special keys
        #(e.g., ESCAPE, RETURN, UP)
        'thrust_key': 'w',
        'left_turn_key': 'a',
        'right_turn_key': 'd',
        'fire_key': 'SPACE',
        'IFF_key': 'j',
        'shots_key': 'k',
        'pnts_key': 'l',
        #Print events to stdout
        'print_events': False,
        #Enable/disable sound
        'sound': True,
        
        
        ### SHIP CONSTANTS ###
        
        #Ship acceleration factor.
        'ship_acceleration': 0.3,
        #Number of hits ship takes before it is destroyed
        'ship_hit_points': 4,
        #Ship's maximum velocity.
        'ship_max_vel': 6,
        #Initial ship orientation.
        'ship_orientation': 90,
        #Initial ship x position.
        'ship_pos_x': 245,
        #Initial ship y position.
        'ship_pos_y': 315,
        #ship collision radius.
        'ship_radius': 3,
        #Ship's turning speed.
        'ship_turn_speed': 6,
        #Initial ship velocity in x direction.
        'ship_vel_x': 0,
        #Initial ship velocity in y direction.
        'ship_vel_y': 0,
        
        
        ### MISSILE CONSTANTS ###
        
        #Maximum number of missiles possible.
        'missile_max': 100,
        #Number of missiles at start of game.
        'missile_num': 100,
        #Points lost when you fire a missile when none remain.
        'missile_penalty': 3,
        #Missile collision radius.
        'missile_radius': 5,
        #Speed of missile fired from ship.
        'missile_speed': 20,
        
        
        ### HEXAGON CONSTANTS ###
        
        #Hex x position.
        'hex_pos_x': 355,
        #Hex y position.
        'hex_pos_y': 315,
        #"Radius" of large hexagon.
        'big_hex': 200,
        #"Radius" of small hexagon.
        'small_hex': 40,
        #Does the outer hex shrink over time?
        'hex_shrink': True,
        #If hex shrinks, to what minimum radius?
        'hex_shrink_radius': 150,
        
        
        ### FORTRESS CONSTANTS ###
        
        #Does the fortress exist?
        'fortress_exists': True,
        #Time in milliseconds it takes the fortress to lock on to the ship before firing.**
        'fortress_lock_time': 1000,
        #Fortress x position.
        'fortress_pos_x': 355,
        #Fortress y position.
        'fortress_pos_y': 315,
        #Fortress collision radius.
        'fortress_radius': 18,
        #Fortress "sector size." Angle of tolerance before fortress turns to face ship.**
        #Bigger means fortress fires more often.
        'fortress_sector_size': 10,
        #Can the fortress be hit if there's a mine onscreen?
        'hit_fortress_while_mine': False,
        #Minimum vulnerability before you can destroy the fortress with a double shot.
        #Note - keep in mind that the first shot of a "double shot" will increase VLNER
        'vlner_threshold': 10,
        #Time in milliseconds that must pass between shots to avoid the fortress'
        #vulnerability to reset
        'vlner_time': 250,
        
                
        ### SHELL CONSTANTS ###
        
        #Speed of shell fired from fortress.
        'shell_speed': 6,
        #Shell collision radius.
        'shell_radius': 3,
        
        
        ### BONUS SYMBOL CONSTANTS ###
        
        #Do bonuses exist? 
        'bonus_exists': True,
        #Randomize bonus position?
        'randomize_bonus_pos': True,
        #Bonus x position.
        'bonus_pos_x': 355,
        #Bonus y position.
        'bonus_pos_y': 390,
        #Probability that next symbol will be the bonus symbol.
        'bonus_probability': 0.3,
        #Bonus symbol.
        'bonus_symbol': '$',
        #Non-bonus symbols. Defaults are # & * % @. Don't use '-', because that's used
        #in the log file to represent that there's no symbol present
        'non_bonus_symbols': ['!', '&', '*', '%', '@'],
        #"Blank time" between symbol appearances in milliseconds**.
        #(Seems like a weird number, but it's to sync with the frame-based original)
        'symbol_down_time': 833,
        #Time in milliseconds each symbol is visible**.
        'symbol_up_time': 2500,
        
        
        ### MINE CONSTANTS ###
        
        #Do mines exists?
        'mine_exists': True,
        #Set mine behavior to standard or MOT
        'mine_mode': 'MOT',
        #Number of foe mines.
        'num_foes': 3,
        #Mine collision radius.
        'mine_radius': 20,
        #Mine speed.
        'mine_speed': 3,
        #Minimum spawn distance. Mine will never appear closer than this distance to the ship
        'minimum_spawn_distance': 200,
        #Maximum spawn distance. Mine will never appear farther away than this distance to the ship
        'maximum_spawn_distance': 700,
        #Minimum time between double-clicks to identify foe mine.
        'intrvl_min': 250,
        #Maximum time between double-clicks to identify foe mine.
        'intrvl_max': 400,
        #Probability that next mine will be a foe.
        'mine_probability': 0.3,
        #Time in milliseconds for a mine to timeout and disappear.
        'mine_timeout': 10000,
        #Time in milliseconds for a mine to spawn.
        'mine_spawn': 5000,
        #Does destroying the fortress reset the mine timer?
        'fortress_resets_mine': True,      
        
        
        ### MOT mines
        
        #Number of mines
        'MOT_count': 5,
        #Time to allow for MOT identification
        'MOT_identification_time': 5000,
        #MOT identification through shots or ship? (i.e., fly into the mine)
        'MOT_identification_type': 'shots',
        #Angle in degrees for the maximum amount a mine can change direction
        'MOT_max_deflection': 15,
        #Time to move mines with IFF info hidden
        'MOT_move_time': 5000,
        #Do MOT mines bounce off walls or warp around edges?
        'MOT_movement_style': 'bounce',
        #Time in between MOT "cycles"
        'MOT_off_time': 5000,
        #Time to display "frozen" MOT mines on onset
        'MOT_onset_time': 3000,
        #Time in between direction changes while MOT mines are moving
        'MOT_switch_time': 1000,
        
        
        ### SCORE CONSTANTS ###
        
        #Use the new scoring system for Flight, Fortress, and Mines? (instead of PNTS, CNTRL, VLCTY and SPEED)
        'new_scoring': True,
        #New scoring position is a more "eye-tracker friendly" format that places the scores around the
        #perimeter of the gameworld, rather than just all along the bottom. Set to f for default positioning
        'new_scoring_pos': True,        
        #Set positions for the display elements. 1 = leftmost for original scoring position
        #for new scoring position, 1 = left item on top row, proceeds clockwise
        #PNTS position(or Flight, for new)
        'PNTS_pos': 1,
        #CNTRL position(or Fortress, for new)
        'CNTRL_pos': 2,
        #VLCTY position(or Mines, for new)
        'VLCTY_pos': 3,
        #VLNER position
        'VLNER_pos': 4,
        #IFF
        'IFF_pos': 5,
        #INTRVL
        'INTRVL_pos': 6,
        #SPEED position(or Bonus, for new)
        'SPEED_pos': 7,
        #SHOTS
        'SHOTS_pos': 8,
        #How often (in milliseconds) the VLCTY and CNTRL scores update (or Flight, for new).
        'update_timer': 1000,
        #Speed at which you're considered to be going "too fast", resulting in a VLCTY
        #point penalty (or Flight, for new).
        'speed_threshold': 4,
        #VLCTY bonus/penalty for going either slow enough or too fast (or Flight, for new).
        'VLCTY_increment': 7,
        #Number of points added to CNTRL score for staying with the hexagons (or Flight, For new).
        #Note that half this number is added when outside the hexagons, so even is recommended.
        'CNTRL_increment': 6,
        #Penalty for colliding with the small hexagon.
        'small_hex_penalty': 5,
        #Penalty for warping around the screen.
        'warp_penalty': 35,
        #Penalty for mine timing out.
        'mine_timeout_penalty': 50,
        #Penalty for mine hitting ship.
        'mine_hit_penalty': 50,
        #Penalty for shell hitting ship.
        'shell_hit_penalty': 50,
        #Penalty for ship destruction.
        'ship_death_penalty': 100,
        #Points for "energizing" a friendly mine.
        'energize_friend': 20,
        #Points for destroying a "foe" mine.
        'destroy_foe': 30,
        #Points for destroying the fortress.
        'destroy_fortress': 100,
        #Points added for selecting points bonus
        'bonus_points': 100,
        #Missiles added for selecting missile bonus
        'bonus_missiles': 50,        
    }

def load_config(config_file):
    config = get_default_config()
    try:
        with open(config_file, 'r') as f:
            config.update(json.load(f))
    except IOError:
        pass
    return config