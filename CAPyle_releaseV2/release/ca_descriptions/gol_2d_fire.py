# Name: Conway's game of life
# Dimensions: 2

# --- Set up executable path, do not edit ---
from logging import config
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



def transition_func(grid, neighbourstates, neighbourcounts, extras):
    state_type = check_state_types(grid)
    combustable_fuel = extras["combustable_fuel"]
    temperature_c = extras["temperature_c"]

    ignite = (neighbourcounts[9] >= 1) & (state_type == "Flammable")
    burning = (grid == 9)
    die_out = ((neighbourcounts[9] + neighbourcounts[12]) >= 8) & (state_type == "Burning") & (combustable_fuel <= 0)
    np.subtract(combustable_fuel, 0.2, out=combustable_fuel, where=burning)
    burned = (grid == 12)

    grid[ignite | burning] = 9
    grid[die_out | burned] = 12

    return grid


def check_state_types(grid):
    state_type = np.full(grid.shape, "Unknown", dtype=object)

    state_type[(FLAMMABLE_STATE_START <= grid) & (grid <= FLAMMABLE_STATE_END)] = "Flammable"
    state_type[(BURNING_STATE_START <= grid) & (grid <= BURNING_STATE_END)] = "Burning"
    state_type[grid == BURNED_STATE] = "Burned"
    state_type[grid == WATER_STATE] = "Water"

    return state_type


def check_fuel(grid, combustable_fuel, state_type):
    die_out = (state_type == "Burning") & (combustable_fuel > 0)
    return die_out


# def apply_wind(grid, wind_direction):
#     # wind_direction is a tuple (dx, dy) indicating the direction of the wind
#     dx, dy = wind_direction
#     shifted_grid = np.roll(grid, shift=dx, axis=0)
#     shifted_grid = np.roll(shifted_grid, shift=dy, axis=1)
#     return shifted_grid

# def apply_temperature(grid, temperature):
#     # Apply temperature effects to the grid
#     # For simplicity, let's say temperature is a scalar that increases the chance of fire
#     fire_chance = 0.1 + 0.1 * temperature
#     # Randomly ignite new fires based on the temperature
#     new_fires = (grid == 1) & (np.random.rand(*grid.shape) < fire_chance)
#     grid[new_fires] = 2
#     return grid

# def change_state(grid, from_state, to_state, condition):
#     # Change cells from from_state to to_state based on a condition
#     grid[(grid == from_state) & condition] = to_state
#     return grid

def setup(args):
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

    config.temperature_grid_c[:] = 25.0  # Default temperature
    config.combustable_fuel_grid[:] = 0.0  # default

    fuel_map = {
        0: 0.5,  # CHAP - LOW
        1: 0.7,  # CHAP - MED
        2: 1.0,  # CHAP - HIGH
        3: 0.6,  # Forest - LOW
        4: 0.8,  # Forest - MED
        5: 1.0,  # Forest - HIGH
        6: 0.4,  # Scrub - LOW
        7: 0.6,  # Scrub - MED
        8: 0.8,  # Scrub - HIGH
    }
    for state, val in fuel_map.items():
        config.combustable_fuel_grid[grid == state] = val

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
        (1.0, 0.2, 0.2),    # BURNING - LOW
        (0.9, 0.1, 0.1),    # BURNING - MED
        (0.7, 0.0, 0.0),    # BURNING - HIGH

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
        "combustable_fuel": config.combustable_fuel_grid
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
