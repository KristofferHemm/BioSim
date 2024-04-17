"""
Example showing how to save images and making a movie of the simulation.
The simulation must be run in image mode in order to create a video.
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
Provide the four (one optional) attributes to BioSim to save images.
img_dir='results'              # Directory to save the image
img_base=f'image_{seed:05d}' # Base filename. All image filenames begin with 'image_<seed>']
img_years=50                   # Image saving interval. 50 means it saves an image every 50 years.
img_fmt='png'                  # Image format. Optional. png is default. 

If any of these values are set to None, then no plots will be shown.
"""
img_dir = 'results'
img_base = f'image_{seed:05d}'
img_years = 1
img_fmt = 'png'

# Remove an already existing directory.
if os.path.isdir(img_dir):
    print("Directory exists. Deleting.")
    shutil.rmtree(img_dir)
sim = BioSim(island_map=geogr,
             ini_pop=initial_fauna,
             seed=seed,
             img_dir=img_dir,
             img_base=img_base,
             img_years=img_years,
             img_fmt=img_fmt)
sim.simulate(10)  # Simulate for 10 years
sim.make_movie()
plt.show(block=True)
