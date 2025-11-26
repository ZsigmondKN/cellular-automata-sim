# Name: Fire simulation
# Dimensions: 2

# --- Set up executable path, do not edit ---
import random
import sys
import inspect
from cautils.noise_grid import generate_multi_region_noise_grid

this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, CAConfig, randomise2d
import capyle.utils as utils
import numpy as np

# State definitions
FLAMMABLE_STATE_START = 0
FLAMMABLE_STATE_END = 8
BURNING_STATE_START = 9
BURNING_STATE_END = 11
BURNED_STATE = 12
WATER_STATE = 13
WET_CHAPARRAL_STATE = 16
CHAPARRAL_STATES = list(range(0, 3)) + [WET_CHAPARRAL_STATE]
FOREST_STATES = range(3, 6)
SCRUB_STATES = range(6, 9)
BURNING_STATES = range(9, 12)
CITY_STATE = 14
DAMAGED_CITY_STATE = 15

# each tick is 3 mins
TICK_SPEED_IN_HOURS = 0.05

# burning durration as outlined in assignments brief
BURN_DURATION_SCRUB_LOW = 1/4
BURN_DURATION_SCRUB_MEDIUM = 2/4
BURN_DURATION_SCRUB_HIGH = 3/4
BURN_DURATION_CHAPARRAL_LOW = 1 * 24/4
BURN_DURATION_CHAPARRAL_MEDIUM = 2 * 24/4
BURN_DURATION_CHAPARRAL_HIGH = 3 * 24/4
BURN_DURATION_FOREST_LOW = 10 * 24/4
BURN_DURATION_FOREST_MEDIUM = 14 * 24/4
BURN_DURATION_FOREST_HIGH = 28 * 24/4

# ignition chance percentage range per tick
IGN_SCALE = 0.4
IGNITION_CHANCE_SCRUB = 47.5 * IGN_SCALE
IGNITION_CHANCE_CHAPARRAL = 35 * IGN_SCALE
IGNITION_CHANCE_FOREST = 7.5 * IGN_SCALE
time_step = 0

# ember chance percentage range per tick
EMBER_CHANCE_SCRUB = 1
EMBER_CHANCE_CHAPARRAL = 2
EMBER_CHANCE_FOREST = 3

# ember distance spread range per tick
EMBER_DISTANCE_SCRUB = (1, 2) # 250m to 500m
EMBER_DISTANCE_CHAPARRAL = (3, 6) # 750m to 1500m
EMBER_DISTANCE_FOREST = (5, 10) # 1.25km to 2.5km

IGNITION_DECREASE_WET = 0.1 # TODO: can we be more scientific about this

def transition_func(grid, neighbourstates, neighbourcounts, extras):

    # tick counter
    global time_step
    time_step += 1

    if (time_step == 1):
        scuffed_init(grid, extras)

    # get initial parameters
    combustable_fuel = extras["combustable_fuel"]
    material_type = extras["material_type"]
    ignition_chance = extras["ignition_chance"]
    state_type = check_state_types(grid)
    density_type = check_density(grid, combustable_fuel, material_type)
    wind_direction = extras["wind_direction_set"]
    ember_is_enabled = extras["ember_set"]

    # update state type
    burning_neighbours = (neighbourcounts[9] + neighbourcounts[10] + neighbourcounts[11]) > 0
    perceptable_to_direct_flame = (burning_neighbours) & (state_type == "Flammable")

    # stage changes
    base_ignite = check_ignite(grid, ignition_chance, perceptable_to_direct_flame, neighbourstates, neighbourcounts, wind_direction)
    if ember_is_enabled:
        ember_ignite = check_ember(grid, state_type, material_type, wind_direction)
        ignite = base_ignite | ember_ignite
    else:
        ignite = base_ignite
    burning = (state_type == "Burning")
    fire_high_density = (ignite | burning) & (density_type == "High")
    fire_medium_density = (ignite | burning) & (density_type == "Medium")
    fire_low_density = (ignite | burning) & (density_type == "Low")
    die_out = (state_type == "Burning") & (combustable_fuel <= 0)
    burned = (state_type == "Burned")

    # Fuel decrease for burning cells
    np.subtract(combustable_fuel, TICK_SPEED_IN_HOURS, out=combustable_fuel, where=burning)

    # update state type
    state_type = check_state_types(grid)
    burning_neighbours = (neighbourcounts[9] + neighbourcounts[10] + neighbourcounts[11]) > 0
    perceptable_to_direct_flame = (burning_neighbours) & (state_type == "Flammable")

    # Update grid
    grid[fire_high_density] = 9
    grid[fire_medium_density] = 10
    grid[fire_low_density] = 11

    grid[die_out | burned] = 12

    if (len(grid[perceptable_to_direct_flame & (grid == CITY_STATE)]) > 0):
            grid[grid == CITY_STATE] = DAMAGED_CITY_STATE
            print(f"Hit City at timestep: {time_step}, hours: {time_step * TICK_SPEED_IN_HOURS}", flush=True)

    # Apply regrowth
    apply_regrowth(grid, neighbourcounts, die_out)

    return grid

def check_ignite(grid, ignition_chance, perceptable_to_direct_flame, neighbourstates, neighbourcounts, wind_direction):
    ignites = np.zeros(ignition_chance.shape, dtype=bool)
    random_draws = np.random.uniform(0, 100, size=perceptable_to_direct_flame.sum())
    wind_multiplier = affected_by_wind(grid, perceptable_to_direct_flame, neighbourstates, wind_direction)
    burning_neighbour_count = neighbourcounts[9] + neighbourcounts[10] + neighbourcounts[11]
    neighbour_multiplier = 1 + (burning_neighbour_count * 0.1)
    ignition_chance_with_multipliers = ignition_chance * wind_multiplier * neighbour_multiplier
    ignites[perceptable_to_direct_flame] = (random_draws < ignition_chance_with_multipliers[perceptable_to_direct_flame])

    failed_to_ignite = perceptable_to_direct_flame & (~ignites)
    ignition_chance[failed_to_ignite] *= 1.10 # increase chance by 10% if failed to ignite

    return ignites

def affected_by_wind(grid, perceptable_to_direct_flame, neighbourstates, wind_direction):
    wind_multiplier = np.zeros(grid.shape, dtype=np.float32)
    wind_multiplier[:] = 1.0 # Base multiplier

    # Neighbor index mapping
    #   0=nw, 1=n, 2=ne, 3=w, 4=e, 5=sw, 6=s, 7=se
    direction_map = {
        "No Wind" :   None,
        "S to N" :    [5, 6, 7], # sw, s, se
        "SW to NE" :  [3, 5, 6], # w, sw, s
        "W to E" :    [0, 3, 5], # nw, w, sw
        "NW to SE" :  [1, 0, 3], # n , nw, w
        "N to S" :    [2, 1, 0], # ne, n, nw
        "NE to SW" :  [4, 2, 1], # e, ne, n
        "E to W":     [7, 4, 2], # se, e, ne
        "SE to NW" :  [6, 7, 4], # s, se, e
    }

    diagonal_winds = {
        "SW to NE",
        "NW to SE",
        "NE to SW",
        "SE to NW",
    }

    main_boost = 5.0 if wind_direction not in diagonal_winds else 2.0

    if wind_direction not in direction_map:
        return wind_multiplier  # No wind effect

    upwind_indices = direction_map[wind_direction]

    diag_flow1 = upwind_indices[0]
    main__flow = upwind_indices[1]
    diag_flow2 = upwind_indices[2]


    wind_multiplier[perceptable_to_direct_flame & (BURNING_STATE_START <= neighbourstates[diag_flow1]) & 
               (neighbourstates[diag_flow1] <= BURNING_STATE_END)] += 0.5
    
    wind_multiplier[perceptable_to_direct_flame & (BURNING_STATE_START <= neighbourstates[main__flow]) & 
               (neighbourstates[main__flow] <= BURNING_STATE_END)] += main_boost
    
    wind_multiplier[perceptable_to_direct_flame & (BURNING_STATE_START <= neighbourstates[diag_flow2]) & 
               (neighbourstates[diag_flow2] <= BURNING_STATE_END)] += 0.5
    return wind_multiplier

def check_ember(grid, state_type, material_type, wind_direction):
    embers_start_on = np.zeros(grid.shape, dtype=bool)
    perceptable_to_embers = (state_type == "Flammable")
    on_fire_scrub = (state_type == "Burning") & (material_type == "Scrub")
    on_fire_chaparral = (state_type == "Burning") & (material_type == "Chaparral")
    on_fire_forest = (state_type == "Burning") & (material_type == "Forest")
    # Create random draws ONLY for the correct number of cells
    random_draws      = np.random.uniform(0, 100, size=grid.shape)
    cells_that_emit_embers_scrub = on_fire_scrub & (random_draws < EMBER_CHANCE_SCRUB)
    cells_that_emit_embers_chaparral = on_fire_chaparral & (random_draws < EMBER_CHANCE_CHAPARRAL)
    cells_that_emit_embers_forest = on_fire_forest & (random_draws < EMBER_CHANCE_FOREST)

    embers_distance_scrub = np.round(np.random.uniform(EMBER_DISTANCE_SCRUB[0], EMBER_DISTANCE_SCRUB[1], size=cells_that_emit_embers_scrub.sum())).astype(int)
    embers_distance_chaparral = np.round(np.random.uniform(EMBER_DISTANCE_CHAPARRAL[0], EMBER_DISTANCE_CHAPARRAL[1], size=cells_that_emit_embers_chaparral.sum())).astype(int)
    embers_distance_forest = np.round(np.random.uniform(EMBER_DISTANCE_FOREST[0], EMBER_DISTANCE_FOREST[1], size=cells_that_emit_embers_forest.sum())).astype(int)

    emitting_indices_scrub = np.argwhere(cells_that_emit_embers_scrub)
    emitting_indices_chaparral = np.argwhere(cells_that_emit_embers_chaparral)
    emitting_indices_forest = np.argwhere(cells_that_emit_embers_forest)
    
    def get_landing_positions(emitting_indices, embers_distance, direction):
        direction_map = {
            "No Wind" : None,
            "S to N" : (-1,  0),
            "N to S" : ( 1,  0),
            "W to E" : ( 0,  1),
            "E to W" : ( 0, -1),
            "SW to NE" : (-1,  1),
            "SE to NW" : (-1, -1),
            "NW to SE" : ( 1,  1),
            "NE to SW" : ( 1, -1),
        }

        if direction not in direction_map:
            dx_unit, dy_unit = (0, 0)  # No embers if no wind direction

        dx_unit, dy_unit = direction_map[direction]

        # Movement scaled by ember distance
        dx = dx_unit * embers_distance
        dy = dy_unit * embers_distance

        landing_x = emitting_indices[:, 0] + dx
        landing_y = emitting_indices[:, 1] + dy

        # Clamp inside grid
        landing_x = np.clip(landing_x, 0, grid.shape[0] - 1)
        landing_y = np.clip(landing_y, 0, grid.shape[1] - 1)

        return landing_x, landing_y
    
    scrub_landing_x, scrub_landing_y = get_landing_positions(emitting_indices_scrub, embers_distance_scrub, wind_direction)
    chaparral_landing_x, chaparral_landing_y = get_landing_positions(emitting_indices_chaparral, embers_distance_chaparral, wind_direction)
    forest_landing_x, forest_landing_y = get_landing_positions(emitting_indices_forest, embers_distance_forest, wind_direction)
    
    # Set embers_start_on at landing positions if perceptable_to_embers is True
    embers_start_on[scrub_landing_x, scrub_landing_y] = perceptable_to_embers[scrub_landing_x, scrub_landing_y]
    embers_start_on[chaparral_landing_x, chaparral_landing_y] = perceptable_to_embers[chaparral_landing_x, chaparral_landing_y]
    embers_start_on[forest_landing_x, forest_landing_y] = perceptable_to_embers[forest_landing_x, forest_landing_y]
    
    return embers_start_on

def check_state_types(grid):
    state_type = np.full(grid.shape, "Unknown", dtype=object)

    state_type[((FLAMMABLE_STATE_START <= grid) & (grid <= FLAMMABLE_STATE_END)) | (grid == CITY_STATE) | (grid == WET_CHAPARRAL_STATE)] = "Flammable"
    state_type[(BURNING_STATE_START <= grid) & (grid <= BURNING_STATE_END)] = "Burning"
    state_type[grid == BURNED_STATE] = "Burned"
    state_type[grid == WATER_STATE] = "Water"

    return state_type

def check_density(grid, combustable_fuel, material_type):
    density_type = np.full(grid.shape, "Unknown", dtype=object)

    density_type[(combustable_fuel < BURN_DURATION_CHAPARRAL_LOW) & (material_type == "Chaparral")] = "Low"
    density_type[(BURN_DURATION_CHAPARRAL_LOW <= combustable_fuel) & (combustable_fuel < BURN_DURATION_CHAPARRAL_MEDIUM) & (material_type == "Chaparral")] = "Medium"
    density_type[(combustable_fuel >= BURN_DURATION_CHAPARRAL_MEDIUM) & (material_type == "Chaparral")] = "High"

    density_type[(combustable_fuel < BURN_DURATION_FOREST_LOW) & (material_type == "Forest")] = "Low"
    density_type[(BURN_DURATION_FOREST_LOW <= combustable_fuel) & (combustable_fuel < BURN_DURATION_FOREST_MEDIUM) & (material_type == "Forest")] = "Medium"
    density_type[(combustable_fuel >= BURN_DURATION_FOREST_MEDIUM) & (material_type == "Forest")] = "High"
    
    density_type[(combustable_fuel < BURN_DURATION_SCRUB_LOW) & (material_type == "Scrub")] = "Low"
    density_type[(BURN_DURATION_SCRUB_LOW <= combustable_fuel) & (combustable_fuel < BURN_DURATION_SCRUB_MEDIUM) & (material_type == "Scrub")] = "Medium"
    density_type[(combustable_fuel >= BURN_DURATION_SCRUB_MEDIUM) & (material_type == "Scrub")] = "High"

    return density_type

def check_fuel(grid, combustable_fuel, state_type):
    die_out = (state_type == "Burning") & (combustable_fuel <= 0)
    return die_out

time_since_gone = 0
specific_gone_time_step = None

def apply_regrowth(grid, neighborcounts, burned_out):
    global time_since_gone, specific_gone_time_step, time_step

    if (specific_gone_time_step is None):
        specific_gone_time_step = np.zeros(grid.shape)

    specific_gone_time_step[burned_out] = time_step

    fire_size = grid[np.isin(grid, BURNING_STATES)]
    
    is_fire_out = len(fire_size) < 2

    if (is_fire_out == False):
        return
    elif(time_since_gone < 30):
        time_since_gone += 1
        return

    # Forest: Full recovery 10-15 years [4]
    # 12.5 med

    # Chap: 7-15 years [4]
    # 11 med

    # Gras: 2-3 years [5]
    # 2.5 med

    # at a scale of 1, each time step 17 days
    # this satisfies the data on the ppt
    regrow_tick_speed = 1

    regrow_probs = {
        0: 1/12.5 * regrow_tick_speed,
        3: 1/11 * regrow_tick_speed,
        6: 1/2.5 * regrow_tick_speed
    }

    # Reset any high density state to low density state (2 -> 0) e.t.c
    init_val = config.initial_grid - (config.initial_grid%3)

    burned_mask = (grid == 12) 

    prob_shape = (time_step - specific_gone_time_step) / 1200
    prob_shape = np.clip(prob_shape, 0, 1)
    
    for veg_type, p in regrow_probs.items():
        effective_p = p * prob_shape          # scale by prob_shape (0–1)
        random_mask = np.random.rand(*grid.shape) < (effective_p * 0.05)

        regrow_mask = burned_mask & random_mask & (init_val == veg_type)
        grid[regrow_mask] = init_val[regrow_mask]

    # Add faster regrowth if parents are grown (seeding and microclimates and the like)
    for veg_type, p in regrow_probs.items():
        count_alive = np.sum(neighborcounts[veg_type:veg_type+3])
        random_mask = np.random.rand(*grid.shape) < (p * count_alive * 0.1)
        regrow_mask = burned_mask & random_mask
        grid[regrow_mask] = veg_type

    # Allow for (slow) growth of low density -> high density
    for veg_type, p in regrow_probs.items():
        alive_mask = (grid == veg_type) | (grid == veg_type+1)
        random_mask = np.random.rand(*grid.shape) < (p * 0.01)
        regrow_mask = alive_mask & random_mask
        grid[regrow_mask] = grid[regrow_mask]+1

config = {}

def setup(args):
    # Share config across the class since i need the initial state for regrowth
    global config
    
    config_path = args[0]
    config = utils.load(config_path)
    # ---THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED---
    regions = [
        # BASE (CHAP)
        {'x': 0, 'y': 0, 'width': 200, 'height': 200, 'min_state': 0, 'max_state': 2, 'seed': 123},

        # FOREST
        {'x': 50, 'y': 20, 'width': 30, 'height': 10, 'min_state': 3, 'max_state': 5, 'seed': 456},
        {'x': 20, 'y': 20, 'width': 30, 'height': 80, 'min_state': 3, 'max_state': 5, 'seed': 789},
        {'x': 20, 'y': 100, 'width': 80, 'height': 40, 'min_state': 3, 'max_state': 5, 'seed': 126},
        
        # WATER
        {'x': 69, 'y': 39, 'width': 12, 'height': 42, 'min_state': WET_CHAPARRAL_STATE, 'max_state': WET_CHAPARRAL_STATE},
        {'x': 70, 'y': 40, 'width': 10, 'height': 40, 'min_state': 13, 'max_state': 13},
        
        {'x': 99, 'y': 159, 'width': 62, 'height': 12, 'min_state': WET_CHAPARRAL_STATE, 'max_state': WET_CHAPARRAL_STATE},
        {'x': 100, 'y': 160, 'width': 60, 'height': 10, 'min_state': 13, 'max_state': 13},
        
        # SCRUB
        {'x': 140, 'y': 40, 'width': 10, 'height': 90, 'min_state': 6, 'max_state': 8, 'seed': 193},

        # CITY
        {'x': 60, 'y': 200-20, 'width': 10, 'height': 10, 'min_state': 14, 'max_state': 14},
        
    ]

    grid = generate_multi_region_noise_grid(shape=(200, 200), regions=regions, global_seed=2025)

    config.initial_initial_grid = grid

    config.title = "Fire Simulation"
    config.dimensions = 2
    config.states = range(17)
    config.wrap = False

    config.state_colors = [
        # CHAP (orange)
        (1.0, 0.7, 0.3),    # CHAP - LOW
        (1.0, 0.5, 0.1),    # CHAP - MED
        (0.8, 0.3, 0.0),    # CHAP - HIGH

        # FOREST (dark green)
        (0.2, 0.5, 0.2),    # Forest - LOW
        (0.1, 0.4, 0.1),    # Forest - MED
        (0.05, 0.25, 0.05), # Forest - HIGH

        # SCRUB (yellow)
        (1.0, 1.0, 0.6),    # Scrub - LOW
        (1.0, 0.9, 0.3),    # Scrub - MED
        (0.9, 0.8, 0.1),    # Scrub - HIGH

        # BURNING (red)
        (1.0, 0.2, 0.2),    # BURNING - HIGH
        (0.9, 0.1, 0.1),    # BURNING - Medium
        (0.7, 0.0, 0.0),    # BURNING - Low

        # BURNED
        (0.15, 0.10, 0.05),

        # WATER
        (0.0, 0.4, 1.0),

        # CITY
        (0.8, 0.8, 0.8),

        # CITY, burned
        (0.82, 0.7, 0.65),

        # Wet chaparral
        (0.6, 0.7, 0.15)
    ]

    init_fire = getattr(config, "initfire", None)
    if init_fire is not None:
        for (x,y) in init_fire:
            config.initial_grid[x,y] = 9

    config.wind_direction_set = getattr(config, "wind_direction_set", "No Wind")
    config.ember_set = getattr(config, "ember_set", True)

    print(f"Selected Wind direction was {config.wind_direction_set}", flush=True)
    print(f"Ember usage was set to {config.ember_set}", flush=True)

    # ----------------------------------------------------------------------
    scuffed_init(grid, {})

    if len(args) == 2:
        config.save()
        sys.exit()

    return config

def scuffed_init(grid, extras):
    global config

    config.combustable_fuel_grid = np.zeros(grid.shape, dtype=np.float32)
    config.material_type_grid = np.full(grid.shape, "Unknown", dtype=object)
    config.ignition_chance_grid = np.zeros(grid.shape, dtype=np.float32)

    config.combustable_fuel_grid[:] = 0.0  # default

    fuel_map = {
        0: BURN_DURATION_CHAPARRAL_LOW,
        1: BURN_DURATION_CHAPARRAL_MEDIUM,
        2: BURN_DURATION_CHAPARRAL_HIGH,
        3: BURN_DURATION_FOREST_LOW,
        4: BURN_DURATION_FOREST_MEDIUM,
        5: BURN_DURATION_FOREST_HIGH,
        6: BURN_DURATION_SCRUB_LOW,
        7: BURN_DURATION_SCRUB_MEDIUM,
        8: BURN_DURATION_SCRUB_HIGH,
        9: BURN_DURATION_CHAPARRAL_LOW,
        10: BURN_DURATION_CHAPARRAL_MEDIUM,
        11: BURN_DURATION_CHAPARRAL_HIGH,
        16: BURN_DURATION_CHAPARRAL_HIGH,
    }

    for state, val in fuel_map.items():
        config.combustable_fuel_grid[grid == state] = val

    config.material_type_grid[np.isin(grid, CHAPARRAL_STATES)] = "Chaparral"
    config.material_type_grid[np.isin(grid, FOREST_STATES)] = "Forest"
    config.material_type_grid[np.isin(grid, SCRUB_STATES)] = "Scrub"

    config.ignition_chance_grid[np.isin(grid, CHAPARRAL_STATES)] = IGNITION_CHANCE_CHAPARRAL
    config.ignition_chance_grid[grid == WET_CHAPARRAL_STATE] = IGNITION_CHANCE_CHAPARRAL*IGNITION_DECREASE_WET
    config.ignition_chance_grid[np.isin(grid, FOREST_STATES)] = IGNITION_CHANCE_FOREST
    config.ignition_chance_grid[np.isin(grid, SCRUB_STATES)] = IGNITION_CHANCE_SCRUB

    extras["combustable_fuel"] = config.combustable_fuel_grid
    extras["material_type"] = config.material_type_grid
    extras["ignition_chance"] = config.ignition_chance_grid

def main():
    # Open the config object
    config = setup(sys.argv[1:])

    extra_attributes = {
        "combustable_fuel": config.combustable_fuel_grid,
        "material_type": config.material_type_grid,
        "ignition_chance": config.ignition_chance_grid,
        "wind_direction_set": config.wind_direction_set,
        "ember_set": config.ember_set
    }

    # Append extra arguments to the transition function
    fire_transition = (transition_func, extra_attributes)

    # Create grid object
    grid = Grid2D(config, fire_transition)

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
