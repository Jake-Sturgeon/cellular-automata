# Name: Conway's game of life
# Dimensions: 2

# --- Set up executable path, do not edit ---
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
import random


def transition_function(grid, neighbourstates, neighbourcounts):
    """Function to apply the transition rules
        and return the new grid"""
    
    pH = 0.3
    pVeg = 0.5
    pDen = 0.5
    pW = 0.5
    p_burn = pH * (1 + pVeg) * (1 + pDen) * pW

    grid[neighbourcounts[1] >= 1 and grid[] == 0] = fire(p_burn)
    
    return grid

def fire(p_burn):
    return p_burn > random.randint(1,101)/100


def setup(args):
    config_path = args[0]
    config = utils.load(config_path)
    # ---THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED---
    config.title = "FIRE!!!!!1"
    config.dimensions = 2
    config.states = (0, 1)
    # ------------------------------------------------------------------------
    
    # ---- Override the defaults below (these may be changed at anytime) ----
    
    config.state_colors = [(0,0,0),(1,0,0)]
    config.num_generations = 150
    config.grid_dims = (200,200)
    
    # ----------------------------------------------------------------------
    
    if len(args) == 2:
        config.save()
        sys.exit()
    
    return config


def main():
    # Open the config object
    config = setup(sys.argv[1:])
    
    # Create grid object
    grid = Grid2D(config, transition_function)
    
    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()
    
    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
