"""
A very simple simulation.
Simple island with all landscape types.
Both Herbivores and Carnivores are present but in opposite corners.
"""

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
sim = BioSim(geogr, initial_fauna, seed=seed)
sim.simulate(50)  # Simulate for 50 years
# You can add more animals to the island mid-simulation
sim.add_population([{'loc': (2, 3),
                     'pop': [{'species': 'Carnivore',
                              'age': 5,
                              'weight': 20}
                             for _ in range(200)]}])
sim.simulate(50)  # Simulate for another 50 years

plt.show(block=True)
