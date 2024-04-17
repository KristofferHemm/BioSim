# -*- coding: utf-8 -*-

import textwrap
import matplotlib.pyplot as plt

from biosim.simulation import BioSim

"""
Compatibility check for BioSim simulations.

This script shall function with biosim packages written for
the INF200 project June 2021.
"""

__author__ = "Hans Ekkehard Plesser, NMBU"
__email__ = "hans.ekkehard.plesser@nmbu.no"


if __name__ == '__main__':

    geogr = """\
               WWWWWWWWWWWWWWWWWWWWW
               WLLLLLLLLLHHHHHHHHHHW
               WLLLLLLLLLHHHHHHHHHHW
               WLLLLLLLLLHHHHHHHHHHW
               WLLLLLLLLLHHHHHHHHHHW
               WLLLLLLLLLHHHHHHHHHHW
               WLLLLLLLLLHHHHHHHHHHW
               WWWWWWWWWWWWWWWWWWWWW"""
    geogr = textwrap.dedent(geogr)

    ini_herbs = [{'loc': (5, 10),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(150)]}]

    sim = BioSim(island_map=geogr, ini_pop=ini_herbs,
                 seed=123456,
                 hist_specs={'fitness': {'max': 1.0, 'delta': 0.05},
                             'age': {'max': 60.0, 'delta': 2},
                             'weight': {'max': 60, 'delta': 2}},
                 cmax_animals={'Herbivore': 300, 'Carnivore': 50},
                 vis_years=1
                 )

    sim.simulate(num_years=100)
    print(sim.year)
    sim.simulate(num_years=100)

    plt.show()