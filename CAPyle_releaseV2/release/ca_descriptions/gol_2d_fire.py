# Name: Conway's game of life
# Dimensions: 2

# --- Set up executable path, do not edit ---
from logging import config
import sys
import inspect
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


def transition_func(grid, neighbourstates, neighbourcounts):
    ignite = (1 <= neighbourcounts[9]) & (grid == 0)
    burning = (grid == 9)
    die_out = (8 <= neighbourcounts[9] + neighbourcounts[12]) & (grid == 9)
    burned = (grid == 12)
    
    grid[:, :] = 0
    grid[ignite | burning] = 9
    grid[die_out | burned] = 12
    return grid

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
    config.title = "Fire Simulation"
    config.dimensions = 2
    config.states = range(14)

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

    # Create grid object
    grid = Grid2D(config, transition_func)

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
