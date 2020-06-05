# --- Set up executable path, do not edit ---
# Team 42
import sys
import inspect
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, randomise2d
from capyle.ca.caconfig import CAConfig
import capyle.utils as utils
import numpy as np
import random
import time
import json

cells = [
         {'id': 0, 'name': 'Chapparal', 'color': (0.741, 0.755, 0.0039), 'flam': 1.7, 'fuel': (48*60)/5, 'mois': 0},
         {'id': 1, 'name': 'Lake', 'color': (0,0,1), 'flam': 0, 'fuel': -20, 'mois': 100},
         {'id': 2, 'name': 'Forest', 'color': (0,1,0), 'flam': 0.3, 'fuel': (30*(24*60))/5, 'mois': 0},
         {'id': 3, 'name': 'Scrubland', 'color': (0.5,0.5,0.5), 'flam': 7, 'fuel': (2*60)/5, 'mois': 0},
         {'id': 4, 'name': 'Fire', 'color': (1, 0, 0), 'flam': 0, 'fuel': 0, 'mois': 0},
         {'id': 5, 'name': 'Burnt', 'color': (0.1, 0.1, 0.1), 'flam': 0, 'fuel': -1, 'mois': 0},
         {'id': 6, 'name': 'DroppedWater', 'color': (0,0,0.75), 'flam': 0, 'fuel': -20, 'mois': 20}
         ]

i = 0

wind_dirs = {
    "NORTH": [0, 0, lambda x: x[0] - 1, lambda x: 0],
    "SOUTH": [0, 0, lambda x: 0, lambda x: x[0] - 1],
    "WEST": [1, 1, lambda x: x[0] - 1, lambda x: 0],
    "EAST": [1, 1, lambda x: 0, lambda x: x[0] - 1],
}

wind_direction = "NORTH"

def setup(args):
    """Set up the config object used to interact with the GUI"""
    config_path = args[0]
    config = utils.load(config_path)
    # -- THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED --
    config.title = "Wildfire Model"
    config.dimensions = 2
    config.wrap = False
    config.num_generations = 600

    config.states = [cell['id'] for cell in cells]
    config.state_colors = [cell['color'] for cell in cells]


    # Make map and scale to grid
    d = 200
    config.grid_dims = (d, d)

    #Grass
    grid = np.zeros((20,20))
    #water
    grid[4:6, 2:6] = 1
    #scrubland
    grid[2:14,13] = 3
    
    
    #Normal dense forest
    grid[12:16,6:10] = 2

#    #dense forest double south
#    grid[12:20,6:10] = 2

#    #dense forest double North
#    grid[8:16,6:10] = 2

#    #Normal dense double  east
#    grid[12:16,6:14] = 2
#
#    #Normal dense double  west
#    grid[12:16,2:10] = 2

    
    
    

    new_grid = np.kron(grid, np.ones((int(d/20),int(d/20))))
#    new_grid[0,new_grid.shape[1]-1] = 4
    new_grid[0,d-1] = 4
#    new_grid[0,0] = 4
    config.initial_grid = new_grid


    # the GUI calls this to pass the user defined config
    # into the main system with an extra argument
    # do not change
    if len(args) == 2:
        config.save()
        sys.exit()
    return config

def transition_function(grid, neighbourstates, neighbourcounts, fuelgrid, flamgrid, moisgrid):
#    water drop
    global i
#    if(i == 48):

#        #bottom of d forest
#        grid[160:200,85:89] = 6
#        flamgrid[160:200,85:89] = flamgrid[160:200,85:89] * 1/cells[6]['mois']

#        #top of d forest
#        grid[40:120,60:62] = 6
#        flamgrid[40:120,60:62] = flamgrid[40:120,60:62] * 1/cells[6]['mois']

#        #Middle of scrub
#        grid[60:62,120:200] = 6
#        flamgrid[60:62,120:200] = flamgrid[60:62,120:200] * 1/cells[6]['mois']

#        #Top of scrub
#        grid[0:40,130:134] = 6
#        flamgrid[0:40,130:134] = flamgrid[0:40,130:134] * 1/cells[6]['mois']

#        #By the town
#        grid[176:180,0:20] = 6
#        grid[180:200,16:20] = 6
#        flamgrid[176:180,0:20] = flamgrid[176:180,0:20] * 1/cells[6]['mois']
#        flamgrid[180:200,16:20] = flamgrid[180:200,16:20] * 1/cells[6]['mois']

    #Update fuels
    on_fire = grid == 4
    fuelgrid[on_fire] = fuelgrid[on_fire] - 1
    burnt = fuelgrid == 0


    #apply wind
    wind = np.ones(grid.shape)
    wind[on_fire] = 1.3
    wind_dir = wind_dirs[wind_direction]
    wind = np.delete(wind, wind_dir[2](wind.shape), axis=wind_dir[0])
    wind = np.insert(wind, wind_dir[3](wind.shape),1, axis=wind_dir[1])

    #Set random fire grid using wind a flamibilty values
    randoms = np.random.rand(grid.shape[0], grid.shape[1])
    new_fires = randoms <= 0.12 * wind * flamgrid

    to_5 = (grid == 4) & ((neighbourcounts[4] + neighbourcounts[5]) >= 8) & (randoms <= 0.008)
    to_5_ash = (grid == 4) & (neighbourcounts[5] >= 1) & (randoms <= 0.008*neighbourcounts[5])
    to_5_water = (grid == 4) & (neighbourcounts[1] >= 1) & (randoms <= 0.25*neighbourcounts[1])
    water_to_ash = (grid == 1) & (neighbourcounts[4] >= 1) & (randoms <= 0.002*neighbourcounts[4] - 0.002*neighbourcounts[1])
    # Don't burn next to water

    #Set things on fire
    not_burning = grid != 4
    not_burnt = grid != 5
    not_water = grid != 1
    to_4 = new_fires & (neighbourcounts[4] >= 1) & not_burning & not_burnt & not_water

    #Update grid
    grid[to_4] = 4
    grid[burnt] = 5
    grid[to_5] = 5
    grid[to_5_ash] = 5
    grid[to_5_water] = 5
    grid[water_to_ash] = 5
    
    
    i += 1
    if (grid[grid.shape[0] - 1][0] == 4):
        print(i)

    return grid

def fuelConfig(grid, config):
    decaygrid = np.zeros(config.grid_dims)
    for i, x in enumerate(cells):
        decaygrid[grid == i] = cells[i]['fuel']
    return decaygrid

def flamConfig(grid, config):
    fgrid = np.zeros(config.grid_dims)
    for i, x in enumerate(cells):
        fgrid[grid == i] = cells[i]['flam']
    return fgrid

def moisConfig(grid, config):
    mgrid = np.zeros(config.grid_dims)
    for i, x in enumerate(cells):
        mgrid[grid == i] = cells[i]['mois']
    return mgrid

def main():
    """ Main function that sets up, runs and saves CA"""
    # Get the config object from set up
    config = setup(sys.argv[1:])



    initial = config.initial_grid
    decaygrid = fuelConfig(initial, config)
    fgrid = flamConfig(initial, config)
    mgrid = moisConfig(initial, config)

    # Create grid object using parameters from config + transition function
    grid = Grid2D(config, (transition_function, decaygrid, fgrid, mgrid))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)


def run_iter(fire_start=(0, 0)):
    config = setup(["temp/config.pkl"])
#    config.initial_grid[0][0] = 0
#    config.initial_grid[0][-1] = 0
    config.initial_grid[fire_start[0]][fire_start[1]] = 4
    initial = config.initial_grid

    dgrid = fuelConfig(initial, config)
    fgrid = flamConfig(initial, config)
    mgrid = moisConfig(initial, config)

    grid = Grid2D(config, (transition_function, dgrid, fgrid, mgrid))

    i = 0
    while grid.grid[-1, 0] != 4:
        grid.step()
        i += 1

    return i

def automated_run():
    data = {}
    for fire_start in [(0, 0), (0, 199)]:
        print('When the fire starts from', fire_start)
        data[fire_start] = []
        for wind in wind_dirs:
            global wind_direction
            wind_direction = wind
            i = run_iter(fire_start=fire_start)
            data[fire_start].append({'wind': wind, 'iter': i})
            print('  It takes the fire {} generations to reach the town with {}ern wind'.format(i, wind.lower()))
    return data

def gather_data():
    while True:
        data = automated_run()
        print(data)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        gather_data()
    else:
        main()
