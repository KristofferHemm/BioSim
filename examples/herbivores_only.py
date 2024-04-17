"""
A very simple simulation.
Simple island with all landscape types.
Herbivores only.
All herbivores start off with age 0 and a random age.
So they should start to die off at first and increase in population afterwards.
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

initial_herbivores = [{'loc': (2, 2),
                       'pop': [{'species': 'Herbivore'}
                               for _ in range(50)]}]

seed = 1234
sim = BioSim(geogr, initial_herbivores, seed=seed)
sim.simulate(50)  # Simulate for 50 years
plt.show(block=True)
