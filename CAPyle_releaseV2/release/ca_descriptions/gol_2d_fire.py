# Name: Conway's game of life
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

FLAMMABLE_STATE_START = 0
FLAMMABLE_STATE_END = 8
BURNING_STATE_START = 9
BURNING_STATE_END = 11
BURNED_STATE = 12
WATER_STATE = 13
CHAPARRAL_STATES = range(0, 3)
FOREST_STATES = range(3, 6)
SCRUB_STATES = range(6, 9)

# each tick is between 1 to 3 hours
# burning durration as outlined in assignments brief
BURN_DURATION_SCRUB_LOW = 1
BURN_DURATION_SCRUB_MEDIUM = 2
BURN_DURATION_SCRUB_HIGH = 3
BURN_DURATION_CHAPARRAL_LOW = 1 * 24
BURN_DURATION_CHAPARRAL_MEDIUM = 2 * 24
BURN_DURATION_CHAPARRAL_HIGH = 3 * 24
BURN_DURATION_FOREST_LOW = 24 * 10
BURN_DURATION_FOREST_MEDIUM = 24 * 20
BURN_DURATION_FOREST_HIGH = 24 * 28

# ignition chance percentage range per tick
IGNITION_CHANCE_SCRUB = 10
IGNITION_CHANCE_CHAPARRAL = 7
IGNITION_CHANCE_FOREST = 2

def transition_func(grid, neighbourstates, neighbourcounts, extras):
    # get initial parameters
    combustable_fuel = extras["combustable_fuel"]
    temperature_c = extras["temperature_c"]
    material_type = extras["material_type"]
    ignition_chance = extras["ignition_chance"]
    state_type = check_state_types(grid)
    density_type = check_density(grid, combustable_fuel, material_type)

    # update state type
    state_type = check_state_types(grid)
    burning_neighbours = (neighbourcounts[9] + neighbourcounts[10] + neighbourcounts[11]) > 0
    perceptable_to_direct_flame = (burning_neighbours) & (state_type == "Flammable")

    # stage changes
    ignite = check_ignite(grid, ignition_chance, perceptable_to_direct_flame, neighbourstates)
    burning = (state_type == "Burning")
    fire_high_density = (ignite | burning) & (density_type == "High")
    fire_medium_density = (ignite | burning) & (density_type == "Medium")
    fire_low_density = (ignite | burning) & (density_type == "Low")
    die_out = (state_type == "Burning") & (combustable_fuel <= 0)
    burned = (state_type == "Burned")

    # Fuel decrease for burning cells
    random_tick_per_cell = np.random.uniform(1, 3, size=combustable_fuel.shape)
    np.subtract(combustable_fuel, random_tick_per_cell, out=combustable_fuel, where=burning)

    # update state type
    state_type = check_state_types(grid)
    burning_neighbours = (neighbourcounts[9] + neighbourcounts[10] + neighbourcounts[11]) > 0
    perceptable_to_direct_flame = (burning_neighbours) & (state_type == "Flammable")

    # Temperature increase for cells influenced by fire
    temperature_increase = np.random.uniform(40, 300, size=perceptable_to_direct_flame.sum())
    temperature_c[perceptable_to_direct_flame] += temperature_increase

    # Update grid
    grid[fire_high_density] = 9
    grid[fire_medium_density] = 10
    grid[fire_low_density] = 11

    grid[die_out | burned] = 12

    # Apply cooling to burned cells
    # TODO: Find another way of tracking when we can regrow
    temperature_decrease = np.random.uniform(1, 2, size=burned.sum())
    temperature_c[burned] -= temperature_decrease

    # Apply regrowth
    apply_regrowth(grid, neighbourcounts, temperature_c)

    return grid

def check_ignite(grid, ignition_chance, perceptable_to_direct_flame, neighbourstates):
    ignites = np.zeros(ignition_chance.shape, dtype=bool)
    random_draws = np.random.uniform(0, 100, size=perceptable_to_direct_flame.sum())
    wind_multiplier = affected_by_wind(grid, perceptable_to_direct_flame, neighbourstates)
    ignition_chance_with_wind = ignition_chance * wind_multiplier
    ignites[perceptable_to_direct_flame] = (random_draws < ignition_chance_with_wind[perceptable_to_direct_flame])

    return ignites

def affected_by_wind(grid, perceptable_to_direct_flame, neighbourstates):
    wind_multiplier = np.zeros(grid.shape, dtype=np.float32)
    wind_multiplier[:] = 1.0 # Base multiplier

    wind_multiplier[perceptable_to_direct_flame & (BURNING_STATE_START <= neighbourstates[0]) & 
               (neighbourstates[0] <= BURNING_STATE_END)] += 0.5
    
    wind_multiplier[perceptable_to_direct_flame & (BURNING_STATE_START <= neighbourstates[1]) & 
               (neighbourstates[1] <= BURNING_STATE_END)] += 10.0
    
    wind_multiplier[perceptable_to_direct_flame & (BURNING_STATE_START <= neighbourstates[2]) & 
               (neighbourstates[2] <= BURNING_STATE_END)] += 0.5
    return wind_multiplier


def check_state_types(grid):
    state_type = np.full(grid.shape, "Unknown", dtype=object)

    state_type[(FLAMMABLE_STATE_START <= grid) & (grid <= FLAMMABLE_STATE_END)] = "Flammable"
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

def apply_regrowth(grid, neighborcounts, temperature):
    # Random chances TODO: what should these be
    regrow_probs = {
        0: 0.04,
        3: 0.02,
        6: 0.1
    }

    # Reset any high density state to low density state (2 -> 0) e.t.c
    init_val = config.initial_initial_grid - (config.initial_initial_grid%3)

    # Only returs on burned cells with a normal temperature
    burned_mask = (grid == 12) & (temperature < 30) 

    # Add spontanious regrowth
    for veg_type, p in regrow_probs.items():
        random_mask = np.random.rand(*grid.shape) < (p * 0.05)
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
        {'x': 70, 'y': 40, 'width': 10, 'height': 40, 'min_state': 13, 'max_state': 13},
        {'x': 100, 'y': 160, 'width': 60, 'height': 10, 'min_state': 13, 'max_state': 13},
        
        # SCRUB
        {'x': 140, 'y': 40, 'width': 10, 'height': 90, 'min_state': 6, 'max_state': 8, 'seed': 193},
    ]

    grid = generate_multi_region_noise_grid(shape=(200, 200), regions=regions, global_seed=2025)

    config.initial_initial_grid = grid

    config.temperature_grid_c = np.zeros(grid.shape, dtype=np.float32)
    config.combustable_fuel_grid = np.zeros(grid.shape, dtype=np.float32)
    config.material_type_grid = np.full(grid.shape, "Unknown", dtype=object)
    config.ignition_chance_grid = np.zeros(grid.shape, dtype=np.float32)

    config.temperature_grid_c[:] = 25.0  # Default temperature
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
    }
    for state, val in fuel_map.items():
        config.combustable_fuel_grid[grid == state] = val

    config.material_type_grid[np.isin(grid, CHAPARRAL_STATES)] = "Chaparral"
    config.material_type_grid[np.isin(grid, FOREST_STATES)] = "Forest"
    config.material_type_grid[np.isin(grid, SCRUB_STATES)] = "Scrub"

    config.ignition_chance_grid[np.isin(grid, CHAPARRAL_STATES)] = IGNITION_CHANCE_CHAPARRAL
    config.ignition_chance_grid[np.isin(grid, FOREST_STATES)] = IGNITION_CHANCE_FOREST
    config.ignition_chance_grid[np.isin(grid, SCRUB_STATES)] = IGNITION_CHANCE_SCRUB

    config.title = "Fire Simulation"
    config.dimensions = 2
    config.states = range(14)
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
        (0,0,0),

        # WATER
        (0.0, 0.4, 1.0)
    ]

    # ----------------------------------------------------------------------

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


def main():
    # Open the config object
    config = setup(sys.argv[1:])

    extra_attributes = {
        "temperature_c": config.temperature_grid_c,
        "combustable_fuel": config.combustable_fuel_grid,
        "material_type": config.material_type_grid,
        "ignition_chance": config.ignition_chance_grid
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
