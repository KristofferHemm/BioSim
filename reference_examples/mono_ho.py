# -*- coding: utf-8 -*-

"""
Island with single lowland cell, only herbivores.
"""


__author__ = 'Hans Ekkehard Plesser, NMBU'


import textwrap
from biosim.simulation import BioSim

geogr = """\
           WWW
           WLW
           WWW"""
geogr = textwrap.dedent(geogr)

ini_herbs = [{'loc': (2, 2),
              'pop': [{'species': 'Herbivore',
                       'age': 5,
                       'weight': 20}
                      for _ in range(50)]}]

for seed in range(100, 103):
    print(seed)
    sim = BioSim(geogr, ini_herbs, seed=seed, vis_years=0,
                 log_file=f'data/mono_ho_{seed:05d}.csv')
    sim.simulate(301)
