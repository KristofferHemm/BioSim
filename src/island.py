"""
Island class.
A grid of the 4 land types: :class:`Water`, :class:`Lowland`,
:class:`Highland`, and :class:`Desert`.
Validates and creates the island.
Handles interaction amongst animals and between the animals and the several landscapes.
Also handles animal migration.

Example
--------
::

    island = Island(geography="WWW\\nWLW\\nWWW")
    island.place_animals({'loc': (2, 2),
                          'pop': [{'species': 'Herbivore',
                                   'age': 5,
                                   'weight': 20},
                                  {'species': 'Carnivore',
                                   'age': 2,
                                   'weight': 10}]
                          })
    island.step()

This code:
    #. Creates an Island object with a 3x3 grid with the provided geography.
    #. Places two animals, one herbivore and 1 carnivore at cell position (2,2)
    #. Steps through the island's cycle.
"""

import random
from typing import Tuple, List, Dict

import numpy as np

from .landscape.desert import Desert
from .landscape.highland import Highland
from .landscape.lowland import Lowland
from .landscape.water import Water


class Island:
    """
    Represents the island under simulation
    """
    # A map of the string text to the landscape class
    cell_map = {"L": Lowland,
                "W": Water,
                "D": Desert,
                "H": Highland}

    def __init__(self, geography: str):
        """
        :param geography: A multiline string depicting the island's geography. See example.
        """
        self.geography = geography
        self.island_map = {}
        self.habitable_map = {}
        self.validate_map()
        self._build_island()

    def to_json(self):
        props = {"geography": self.geography,
                 "island_map": {str(coords): cell.to_json()
                                for coords, cell in self.island_map.items()}}
        return props

    def validate_map(self):
        """
        Validate the map cells, map shape and water border.
        Raises a Value error otherwise.
        """

        for cell_type in list(set(list(self.geography.replace('\n', '')))):
            if cell_type not in self.cell_map.keys():
                raise ValueError(f"Invalid cell type: {cell_type}")

        def get_distinct(items: list) -> str:
            # Helper method to return the unique characters in a list
            return "".join(list(set(items)))

        geo_split = self.geography.split("\n")

        # Validate shape of geography
        if len(set([len(line) for line in geo_split])) != 1:
            raise ValueError("Not all rows of the Island are of the same size.")

        # Validate top row is water
        if get_distinct(top_row := list(geo_split[0])) != "W":
            raise ValueError(f"Top row is not all water: {''.join(top_row)}")

        # Validate bottom row is water
        if get_distinct(bottom_row := list(geo_split[-1])) != "W":
            raise ValueError(f"Bottom row is not all water: {''.join(bottom_row)}")

        # Validate leftmost column is water
        if get_distinct(left_col := [line[0] for line in geo_split]) != "W":
            raise ValueError(f"Leftmost column is not all water: {''.join(left_col)}")

        # Validate rightmost column is water
        if get_distinct(right_col := [line[-1] for line in geo_split]) != "W":
            raise ValueError(f"Rightmost column is not all water: {''.join(right_col)}")

    def _build_island(self):
        """
        Build the island map with objects of the several landscape types.
        """
        self.island_map = {(i + 1, j + 1): self.cell_map[y]()
                           for i, x in enumerate(self.geography.split("\n"))
                           for j, y in enumerate(x)}
        # Create a separate habitable map for faster iteration through the island
        self.habitable_map = {coord: cell
                              for coord, cell in self.island_map.items() if cell.is_habitable}

    @property
    def shape(self) -> Tuple:
        """
        :return: shape of the island
        """
        return max(list(self.island_map.keys()))

    def place_animals(self, population: List):
        """
        Place the animals in the land cells.

        :param population: List of a dictionary containing the location and list of
                           animals to add to that location.
                           Example:
                           [{'loc': (2, 2),
                           'pop': [{'species': 'Herbivore', 'age': 1, 'weight': 10.},
                           {'species': 'Herbivore', 'age': 2, 'weight': 20.}]}]
        """
        for pop in population:
            loc = pop['loc']
            for animal in pop['pop']:
                self.island_map[loc].add_animal(animal)

    def step(self):
        """
        Step through the island's annual cycle.
            1. Feeding
            2. Birth
            3. Migration
            4. Aging
            5. Weight loss
            6. Death

        The fodder resets at the beginning of every cycle.
        All steps happen at an animal level, except migration which happens on the island level.
        """
        for cell in self.habitable_map.values():
            cell.reset_fodder()
            cell.feed()
            cell.birth()

        self.migrate()
        for cell in self.habitable_map.values():
            cell.aging()
            cell.lose_weight()
            cell.die()

    @property
    def num_animals(self) -> int:
        """
        :return: The number of animals in all cells of the island.
        """
        pop = 0
        for value in self.habitable_map.values():
            pop += value.num_animals
        return pop

    @property
    def num_animals_per_species(self) -> Dict[str, int]:
        """
        :return: Dictionary of key animal species and value counts.
        """
        num_c = 0
        num_h = 0
        for cell in self.habitable_map.values():
            num_c += cell.num_herbivores
            num_h += cell.num_carnivores
        return {"Herbivore": num_c,
                "Carnivore": num_h}

    move_direction_map = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def migrate(self):
        """
        Migration of the animals to neighbouring cells.
        Animals can only migrate once per cycle.
        Animals can randomly migrate to the 4 neighbouring, non-diagonal cells.
        """
        # A holding list to prevent animals migrating twice a year.
        migration = []
        for coord, landtypes in self.habitable_map.items():
            for animal in landtypes.get_migrations():
                direction = random.choice(self.move_direction_map)
                new_coord = tuple(np.sum([coord, direction], axis=0))
                if self.island_map[new_coord].is_habitable:
                    if direction == (-1, 0) or direction == (0, -1):
                        # If the direction is up or left, move the animal immediately.
                        self.island_map[new_coord].place_animal(animal)
                        self.island_map[coord].remove_animal(animal)
                    else:
                        # Else set them to migrate at the end.
                        migration.append({"from": coord, "to": new_coord, 'animal': animal})
        # Migrate animals
        for x in migration:
            self.island_map[x['to']].place_animal(x['animal'])
            self.island_map[x['from']].remove_animal(x['animal'])

    def _get_current_population_state(self, species) -> np.ndarray:
        """
        Return the population of the species for each cell on the island.

        :param species: species to return population of
        :return: numpy array with the herbivore population of the island
        """
        population_state = np.zeros(self.shape)
        for coords, cell in self.island_map.items():
            # Island coordinates start from (1,1). Reduce by 1 for numpy compatibility.
            population_state[tuple(np.array(coords) - 1)] = cell.num_animals_per_species[species]
        return population_state

    def get_current_herbivore_population_state(self):
        """
        :return: a numpy array with the herbivore population of the island
        """
        return self._get_current_population_state('Herbivore')

    def get_current_carnivore_population_state(self):
        """
        Return the population for each cell on the island.
        :return: a numpy array with the carnivore population of the island
        """
        return self._get_current_population_state('Carnivore')

    def _get_current_animal_properties(self, species: str, prop: str) -> list:
        """
        Return the property of the animals for each cell on the island
        Use the `getattr` to make it dynamic. No performance loss observed on benchmark.

        :param species: species to return properties of. herbivores or carnivores
        :param prop: property to return. age, weight or fitness.
        :return: numpy array of properties
        """
        props = []
        for cell in self.island_map.values():
            props += getattr(cell, f"get_all_{prop}")(
                species)  # props+=baseland.get_all_fitness('herbivores')
        return props

    def get_current_herbivore_fitness(self):
        """
        :return: fitness of all herbivores on the island
        """
        return self._get_current_animal_properties('herbivores', 'fitness')

    def get_current_carnivore_fitness(self):
        """
        :return: fitness of all carnivores on the island
        """
        return self._get_current_animal_properties('carnivores', 'fitness')

    def get_current_herbivore_weight(self):
        """
        :return: weight of all herbivores on the island
        """
        return self._get_current_animal_properties('herbivores', 'weight')

    def get_current_carnivore_weight(self):
        """
        :return: weight of all carnivores on the island
        """
        return self._get_current_animal_properties('carnivores', 'weight')

    def get_current_herbivore_age(self):
        """
        :return: age of all herbivores on the island
        """
        return self._get_current_animal_properties('herbivores', 'age')

    def get_current_carnivore_age(self):
        """
        :return: age of all carnivores on the island
        """
        return self._get_current_animal_properties('carnivores', 'age')
