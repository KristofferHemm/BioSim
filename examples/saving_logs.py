"""
Example showing how to save log files.
The project can save a csv file for a simulation with the following fields:
 * Year : Year of the simulation
 * Population : Total number of animals on the island
 * Herbivores : Total number of Herbivores on the island
 * Carnivores : Total number of Carnivores on the island
"""
import shutil
import os
import textwrap

import matplotlib.pyplot as plt
from biosim.simulation import BioSim

geogr = """\
           WWWWW
           WDLDW
           WLHLW
           WDLDW
           WWWWW"""
geogr = textwrap.dedent(geogr)

initial_fauna = [{'loc': (2, 3),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(50)]},
                 {'loc': (2, 3),
                  'pop': [{'species': 'Carnivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(20)]}]
seed = 1234
"""
Provide the following parameter to Biosim to save logs as a CSV. 
log_file='data/logs.csv' # Will save the simulation data to the logs.csv file in the data directory.
"""

log_file = 'data/logs.csv'

# Remove an already existing directory.
dir_name = log_file.split("/")[-2]
if os.path.isdir(dir_name):
    print("Directory exists. Deleting.")
    shutil.rmtree(dir_name)
sim = BioSim(island_map=geogr,
             ini_pop=initial_fauna,
             seed=seed,
             log_file=log_file)
sim.simulate(50)  # Simulate for 50 years
plt.show(block=True)
