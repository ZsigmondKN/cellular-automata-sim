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
    # dead = state == 0, live = state == 1
    # unpack state counts for state 0 and state 1
    dead_neighbours, live_neighbours, sick_neighbors = neighbourcounts
    # create boolean arrays for the birth & survival rules
    # if 3 live neighbours and is dead -> cell born
    birth = ((live_neighbours + sick_neighbors) == 3) & (grid == 0)
    # if 2 or 3 live neighbours and is alive -> survives
    survive = ((live_neighbours == 2) | (live_neighbours == 3)) & (grid == 1)
    sick = ((grid == 1) & (sick_neighbors > 2)) | ((grid == 2) & ((sick_neighbors + live_neighbours) > 0))
    death_by_sick = ((grid == 2) & (sick_neighbors > 4))

    # Set all cells to 0 (dead)
    grid[:, :] = 0
    # Set cells to 1 where either cell is born or survives
    grid[birth | survive] = 1
    grid[sick] = 2
    grid[death_by_sick] = 0
    return grid


def setup(args):
    config_path = args[0]
    config = utils.load(config_path)
    # ---THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED---
    preset_grid = np.zeros((10, 10))
    preset_grid[3:6, 3:6] = 1   # small 3x3 block of state 1
    preset_grid[7, 2:5] = 2     # a stripe of state 2

    config.initial_grid = preset_grid


    config.title = "Fire Simulation"
    config.dimensions = 2
    config.states = range(27)
    # ------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    config.state_colors = [
        # CHAP (orange)
        (1.0, 0.7, 0.3),  # CHAP - NB - LOW
        (1.0, 0.5, 0.1),  # CHAP - NB - MED
        (0.8, 0.3, 0.0),  # CHAP - NB - HIGH
        (1.0, 0.2, 0.2),  # CHAP - B - LOW (vibrant red)
        (0.9, 0.1, 0.1),  # CHAP - B - MED
        (0.7, 0.0, 0.0),  # CHAP - B - HIGH

        # BURNED
        (0,0,0),

        # UNUSED
        (1,1,1),

        # WATER
        (0.0, 0.4, 1.0),

        # FOREST (dark green)
        (0.2, 0.5, 0.2),  # Forest - NB - LOW
        (0.1, 0.4, 0.1),  # Forest - NB - MED
        (0.05, 0.25, 0.05),# Forest - NB - HIGH
        (1.0, 0.2, 0.2),  # Forest - B - LOW (vibrant red)
        (0.9, 0.1, 0.1),  # Forest - B - MED
        (0.7, 0.0, 0.0),  # Forest - B - HIGH

        # BURNED
        (0,0,0),

        # UNUSED
        (1,1,1), (1,1,1),

        # SCRUB (yellow)
        (1.0, 1.0, 0.6),  # Scrub - NB - LOW
        (1.0, 0.9, 0.3),  # Scrub - NB - MED
        (0.9, 0.8, 0.1),  # Scrub - NB - HIGH
        (1.0, 0.2, 0.2),  # Scrub - B - LOW (vibrant red)
        (0.9, 0.1, 0.1),  # Scrub - B - MED
        (0.7, 0.0, 0.0),  # Scrub - B - HIGH

        # BURNED
        (0,0,0),

        # UNUSED
        (1,1,1), (1,1,1)
    ]

    # config.num_generations = 150
    # config.grid_dims = (200,200)

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
