"""
Simulate the island.
The BioSim class allows you to create the island, place the animals
and carry out the simulation for the fauna. It also gives you the option to
add animals mid-simulation, visualize the simulation and save the simulation as a video.
Example
--------
::

    geography="WWW\\nWLW\\nWWW"
    sim = BioSim(geography,
                 seed = 1234,
                 ini_pop = {'loc': (2, 2),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 20},
                          {'species': 'Carnivore',
                           'age': 2,
                           'weight': 10}]
                  })
    sim.simulate(50)  # Simulate 50 years.

Refer to examples directory for more detailed implementations.
"""
# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2021 Hans Ekkehard Plesser / NMBU
import json
import random

from .animals.carnivore import Carnivore
from .animals.herbivore import Herbivore
from .landscape.lowland import Lowland
from .landscape.highland import Highland
from .landscape.desert import Desert
from .landscape.water import Water
from .island import Island
from pathlib import Path
import ffmpeg
import pandas as pd

from .state_loader import StateLoader
from .plotter import Plotter

species_dict = {"Herbivore": Herbivore, "Carnivore": Carnivore}
landscape_dict = {"L": Lowland, "H": Highland, "D": Desert, "W": Water}


class BioSim:
    """
    Implements the simulation of the Island.
    """

    def __init__(self, island_map, ini_pop, seed,
                 vis_years=1, ymax_animals=None, cmax_animals=None, hist_specs=None,
                 img_dir=None, img_base=None, img_fmt='png', img_years=None,
                 log_file=None):
        """
        :param island_map: Multi-line string specifying island geography
        :param ini_pop: List of dictionaries specifying initial population
        :param seed: Integer used as random number seed
        :param ymax_animals: Number specifying y-axis limit for graph showing animal numbers
        :param cmax_animals: Dict specifying color-code limits for animal densities
        :param hist_specs: Specifications for histograms, see below
        :param vis_years: years between visualization updates (if 0, disable graphics)
        :param img_dir: String with path to directory for figures
        :param img_base: String with beginning of file name for figures
        :param img_fmt: String with file type for figures, e.g. 'png'
        :param img_years: years between visualizations saved to files (default: vis_years)
        :param log_file: If given, write animal counts to this file

        If ymax_animals is None, the y-axis limit should be adjusted automatically.
        If cmax_animals is None, sensible, fixed default values should be used.
        cmax_animals is a dict mapping species names to numbers, e.g.,

            {'Herbivore': 50, 'Carnivore': 20}

        hist_specs is a dictionary with one entry per property for which a histogram shall be shown.
        For each property, a dictionary providing the maximum value and the bin width must be
        given, e.g.,

            {'weight': {'max': 80, 'delta': 2}, 'fitness': {'max': 1.0, 'delta': 0.05}}

        Permitted properties are 'weight', 'age', 'fitness'.


        If img_dir is None, no figures are written to file. Filenames are formed as

            f'{os.path.join(img_dir, img_base}_{img_number:05d}.{img_fmt}'

        where img_number are consecutive image numbers starting from 0.

        img_dir and img_base must either be both None or both strings.
        """
        self.island_map = island_map
        self.ini_pop = ini_pop
        self.seed = seed
        random.seed(self.seed)

        self.island = Island(self.island_map)
        self.add_population(self.ini_pop)
        self.vis_years = vis_years
        self.img_dir = img_dir
        self.img_base = img_base
        self.img_fmt = img_fmt
        self.img_years = img_years if img_years else vis_years
        self.log_file = log_file
        self.create_result_directory()

        self.num_years_simulated = 0
        self.history = []
        self.cmax_animals = cmax_animals
        self.ymax_animals = ymax_animals
        self.hist_specs = hist_specs
        self.figure_number = 0
        self.plotter = self._create_plotter()

    def to_json(self):
        props = {"island_map": self.island_map,
                 "seed": self.seed,
                 "island": self.island.to_json(),
                 "vis_years": self.vis_years,
                 "img_dir": self.img_dir,
                 "img_base": self.img_base,
                 "img_fmt": self.img_fmt,
                 "img_years": self.img_years,
                 "log_file": self.log_file,
                 "num_years_simulated": self.num_years_simulated,
                 "cmax_animals": self.cmax_animals,
                 "ymax_animals": self.ymax_animals,
                 "hist_specs": self.hist_specs,
                 "ini_pop": []
                 }
        return props

    def _create_plotter(self):
        """Create a plotter object only if the vis_years parameter is set"""
        if self.vis_years:
            return Plotter(island=self.island,
                           heatmap_vmax=self.cmax_animals,
                           y_max=self.ymax_animals,
                           hist_specs=self.hist_specs,
                           img_dir=self.img_dir,
                           img_base=self.img_base,
                           img_fmt=self.img_fmt)

    def create_result_directory(self):
        """
        Create the result directory for images, video and log file if they don't exist
        """
        if self.img_dir:
            img_dir = Path(self.img_dir)
            if not img_dir.is_dir():
                print(f"Images directory: '{img_dir.resolve()}' does not exist. Creating.")
                img_dir.mkdir(parents=True, exist_ok=True)

        if self.log_file:
            log_file = Path(self.log_file)
            parent_dir = log_file.parent
            if not parent_dir.is_dir():
                print(f"Log directory '{parent_dir.resolve()}' does not exist. Creating.")
                parent_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def set_animal_parameters(species, params):
        """
        Set parameters for animal species.

        :param species: String, name of animal species
        :param params: Dict with valid parameter specification for species
        """
        species_dict[species].set_params(params)

    @staticmethod
    def set_landscape_parameters(landscape, params):
        """
        Set parameters for landscape type.

        :param landscape: String, code letter for landscape
        :param params: Dict with valid parameter specification for landscape
        """
        landscape_dict[landscape].set_params(params)

    def simulate(self, num_years):
        """
        Run simulation while visualizing the result.

        :param num_years: number of years to simulate
        """
        for year in range(num_years):
            animal_population = self.num_animals_per_species
            self.history.append({"year": self.year,
                                 "population": self.num_animals,
                                 "herbivores": animal_population['Herbivore'],
                                 "carnivores": animal_population['Carnivore']})
            self.update_plot()
            self.save_plot()
            self.island.step()
            self.save_logs()
            self.num_years_simulated += 1

    def save_logs(self):
        if self.log_file:
            df = pd.DataFrame(self.history)
            df.to_csv(self.log_file, sep='\t', index=False)

    def add_population(self, population):
        """
        Add a population to the island

        :param population: List of dictionaries specifying population
        """
        self.island.place_animals(population)

    def update_plot(self):
        """
        Update the plot with new simulation results.
        """
        if self.vis_years and self.num_years_simulated % self.vis_years == 0:
            self.plotter.update_figures(history=self.history)

    def save_plot(self):
        """
        Save the figure to a file.
        self.img_base, self.img_dir and self.img_fmt must be provided.
        """
        if self.img_years and self.img_base and self.img_dir and self.img_fmt and \
                self.num_years_simulated % self.img_years == 0:
            self.plotter.save_fig(self.figure_number)
            self.figure_number += 1

    @property
    def year(self):
        """Last year simulated."""
        return self.num_years_simulated

    @property
    def num_animals(self):
        """Total number of animals on island."""
        return self.island.num_animals

    @property
    def num_animals_per_species(self):
        """Number of animals per species in island, as dictionary."""
        return self.island.num_animals_per_species

    def make_movie(self):
        """Create MPEG4 movie from visualization images saved."""
        ffmpeg.input(
            Path(self.img_dir) / Path(self.img_base + "_%05d." + self.img_fmt),
            framerate=10).output(f'{self.img_base}.mp4').overwrite_output().run()

    def save_state(self):
        """
        Save simulation state
        The state file will be saved only if log_file is provided.
        The state file will have the same file name as the log_file, but with a .json
        extension.
        The history CSV is saved first.
        """
        self.save_logs()
        if self.log_file:
            new_filename = Path(self.log_file).with_suffix('.json')
            with open(new_filename, 'w') as outfile:
                json.dump(self.to_json(), outfile, indent=4)
        else:
            raise ValueError("log_dir not provided. State was not saved.")

    @classmethod
    def load_state(cls, log_file):
        """
        Load the simulation state from a JSON file
        :param log_file: path of the state file
        :return: BioSom object
        """
        json_filename = Path(log_file).with_suffix('.json')
        return StateLoader.load_from_json(json_filename, log_file)
