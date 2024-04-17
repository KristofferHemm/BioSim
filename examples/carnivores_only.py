"""
A very simple simulation.
Simple island with all landscape types.
Carnivores only.
Since there are no herbivores to eat, the carnivores should die down pretty quickly.
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

initial_carnivores = [{'loc': (2, 2),
                      'pop': [{'species': 'Carnivore'}
                              for _ in range(50)]}]

seed = 1234
sim = BioSim(geogr, initial_carnivores, seed=seed)
sim.simulate(50)  # Simulate for 50 years
plt.show(block=True)
