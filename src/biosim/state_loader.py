"""
Implements loading the simulation state from file
"""
import ast
import json

import pandas as pd
from biosim.island import Island
from biosim.animals.herbivore import Herbivore
from biosim.animals.carnivore import Carnivore
from biosim.landscape.lowland import Lowland
from biosim.landscape.highland import Highland
from biosim.landscape.water import Water
from biosim.landscape.desert import Desert

landtype_mapping = {'lowland': Lowland,
                    'water': Water,
                    'highland': Highland,
                    'desert': Desert}
animal_map = {"herbivore": Herbivore,
              "carnivore": Carnivore}

simulation_attributes = ["island_map", "seed", "vis_years", "img_dir", "img_base", "img_fmt",
                         "img_years", "log_file", "cmax_animals",
                         "ymax_animals", "hist_specs", "ini_pop"]
animal_attributes = ['age', 'weight']


class StateLoader:
    """
    Loads simulation state from file
    """

    @staticmethod
    def read_json(state_file):
        """
        Read the State JSON file and return the json object
        :param state_file: State JSON file
        :return: JSON object
        """
        with open(state_file) as json_file:
            data = json.load(json_file)
        return data

    @staticmethod
    def load_from_json(biosim_json_file, history_csv_file):
        """
        Read the state files from disk and return a state-loaded BioSim object
        :param biosim_json_file: filepath of the BioSim state JSON file
        :param history_csv_file: filepath of the BioSim history CSV file
        :return: BioSim object
        """
        # Import BioSim here to avoid recursive import error
        from biosim.simulation import BioSim

        # Read the state json file
        biosim_json = StateLoader.read_json(biosim_json_file)

        # Create the BioSim obj
        sim = BioSim(
            **{key: value for key, value in biosim_json.items() if key in simulation_attributes})
        sim.num_years_simulated = biosim_json['num_years_simulated']

        # Load the Island state and add it to the simulation object
        sim.island = StateLoader.load_island(biosim_json['island'])
        # Reset the plotter island object only if it exists.
        # if vis_years was None, then this would not have been created.
        if sim.plotter:
            sim.plotter.island = sim.island
        # Read and add the history for continued graphs.
        df = pd.read_csv(history_csv_file, sep='\t')
        sim.history = df.to_dict(orient='records')
        return sim

    @staticmethod
    def load_island(island):
        """
        Create an Island object from JSON
        :param island: JSON state of the Island
        :return: Island Object
        """
        geography = island.get("geography")
        island_map = {}
        # Read the island map data from JSON
        for coords, cell in island.get("island_map").items():
            obj_ = landtype_mapping[cell['landtype']]()
            obj_.fodder = cell['fodder']
            obj_.set_params({'f_max': cell['f_max']})
            obj_.herbivores = [StateLoader.build_animal(h) for h in cell['herbivores']]
            obj_.carnivores = [StateLoader.build_animal(c) for c in cell['carnivores']]
            island_map[ast.literal_eval(coords)] = obj_
        island = Island(geography)
        island.island_map = island_map
        # Reset the habitable map
        island.habitable_map = {coord: cell
                                for coord, cell in island.island_map.items() if cell.is_habitable}
        return island

    @staticmethod
    def build_animal(animal_json):
        """
        Create an Animal object from JSON
        :param animal_json: JSON state of the Animal
        :return: Animal object
        """
        animal = animal_map[animal_json['species']](**{x: animal_json[x]
                                                       for x in animal_attributes})
        animal._fitness = animal_json['fitness']
        animal.is_dead = animal_json['is_dead']
        animal.set_params(
            {x: animal_json[x] for x in animal_attributes if x not in animal_attributes})
        return animal
