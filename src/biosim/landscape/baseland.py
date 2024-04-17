from typing import List, Union, Dict
from itertools import chain
from biosim.animals.carnivore import Carnivore
from biosim.animals.herbivore import Herbivore
import random

animal_map = {"Herbivore": Herbivore,
              "Carnivore": Carnivore}


class Baseland:
    """
    Describes a single cell. Defines the base attributes and properties for other land types.
    """
    # Class Parameters
    f_max = 0
    default_params = {"f_max": f_max}

    def __init__(self, herbivores: List[Herbivore] = None, carnivores: List[Carnivore] = None):
        """

        :param herbivores: List of herbivores located in the cell
        :param carnivores: List of herbivores located in the cell
        """
        self.fodder = self.f_max
        self.landtype = None
        self.is_habitable = True
        self.herbivores = herbivores if herbivores else []
        self.carnivores = carnivores if carnivores else []

    def to_json(self):
        props = {"fodder": self.fodder,
                 "landtype": self.landtype,
                 "is_habitable": self.is_habitable,
                 "herbivores": [h.to_json() for h in self.herbivores],
                 "carnivores": [c.to_json() for c in self.carnivores]}
        props.update(
            {key: getattr(self, key) for key, value in self.default_params.items()})
        return props

    @property
    def num_animals(self):
        """Total number of animals in the cell"""
        return len(self.herbivores) + len(self.carnivores)

    @property
    def num_animals_per_species(self):
        """Total number of animals per species in the cell"""
        return {"Herbivore": len(self.herbivores),
                "Carnivore": len(self.carnivores)}

    @property
    def num_herbivores(self):
        """Total number of herbivores in the cell"""
        return len(self.herbivores)

    @property
    def num_carnivores(self):
        """Total number of carnivores in the cell"""
        return len(self.carnivores)

    @classmethod
    def set_params(cls, params: Dict[str, Union[int, float]]):
        """
        Set the parameters of the class.

        :param params: Parameters to be updated
        """
        for key, value in params.items():
            if key not in cls.default_params.keys():
                raise ValueError(f"Invalid parameter: {key}")
            if not (type(value) == float or type(value) == int):
                raise ValueError(f"Value {value} for key {key} is not a float or an integer.")
        for key, value in params.items():
            setattr(cls, key, value)

    @classmethod
    def reset_params(cls):
        """
        Reset the parameters of the animal
        """
        for key, value in cls.default_params.items():
            setattr(cls, key, value)

    def add_animal(self, animal: Dict[str, int]):
        """
        Add animal to the cell

        :param animal: Dictionary of structure {'species': 'Herbivore', 'age': 1, 'weight': 10.}
        """
        if animal['species'] not in ["Herbivore", "Carnivore"]:
            raise ValueError(f"Invalid animal type: {animal['species']}")
        animal_obj = animal_map[animal['species']](age=animal.get('age', 0),
                                                   weight=animal.get('weight', None))
        self.place_animal(animal_obj)

    def place_animal(self, animal_obj: Union[Herbivore, Carnivore]):
        """
        Place the animal object into the cell

        :param animal_obj: Animal object to place.
        """
        if animal_obj.species == "herbivore":
            self.herbivores.append(animal_obj)
        else:
            self.carnivores.append(animal_obj)

    def remove_animal(self, animal_obj: Union[Herbivore, Carnivore]):
        """
        Remove an animal from the cell.

        :param animal_obj: Animal object to remove.
        """
        if animal_obj.species == "herbivore":
            self.herbivores.remove(animal_obj)
        else:
            self.carnivores.remove(animal_obj)

    def feed_herbivores(self):
        """
        Feed herbivores with the fodder until no fodder remains.
        """
        # Herbivores feed in decreasing order of fitness
        for animal in sorted(self.herbivores, key=lambda h: h.fitness, reverse=True):
            if self.fodder > 0:
                eaten = animal.feeding(self.fodder)
                self.fodder -= eaten
            else:
                break

    def feed_carnivores(self):
        """
        Feed carnivores with herbivores.
        """
        # The Carnivores feed in random order.
        random.shuffle(self.carnivores)
        # The Carnivores feed on the Herbivores in increasing order of fitness.
        self.herbivores = sorted(self.herbivores, key=lambda h: h.fitness)
        # One Carnivore hunts at a time
        for carn in self.carnivores:
            self.herbivores = carn.eat_herbivores(self.herbivores)

    def feed(self):
        """
        Feed herbivores with fodder.
        Feed carnivores with Herbivores
        """
        self.feed_herbivores()
        self.feed_carnivores()

    def birth(self):
        """
        Animals give birth
        """

        def give_birth(animals: List[Union[Herbivore, Carnivore]]):
            return [child for animal in animals if (child := animal.give_birth(len(animals)))]

        if len(self.herbivores) > 1:
            self.herbivores += give_birth(self.herbivores)
        if len(self.carnivores) > 1:
            self.carnivores += give_birth(self.carnivores)

    def aging(self):
        """Age all animals"""
        for animal in chain(self.herbivores, self.carnivores):
            animal.aging()

    def lose_weight(self):
        """All animals lose weight """
        for animal in chain(self.herbivores, self.carnivores):
            animal.lose_weight()

    def die(self):
        """
        Check if animals survive the year.
        Only store animals that are still alive
        """
        self.herbivores = [herb for herb in self.herbivores if not herb.death()]
        self.carnivores = [carn for carn in self.carnivores if not carn.death()]

    def reset_fodder(self):
        """Reset the fodder to the maximum value"""
        self.fodder = self.f_max

    def get_migrations(self) -> list:
        """
        Return the list of all animals that will migrate to a neighbouring cell
        """
        return [animal for animal in chain(self.herbivores, self.carnivores) if animal.migrate()]

    def step(self):
        """Step through a single year"""
        self.reset_fodder()
        self.feed()
        self.birth()
        self.aging()
        self.lose_weight()
        self.die()

    def get_all_fitness(self, species) -> list:
        """
        Return the fitness of all animals in the cell by species
        """
        animals = {'herbivores': self.herbivores, 'carnivores': self.carnivores}
        return [animal.fitness for animal in animals[species]]

    def get_all_weight(self, species) -> list:
        """
        Return the weight of all animals in the cell by species
        """
        animals = {'herbivores': self.herbivores, 'carnivores': self.carnivores}
        return [animal.weight for animal in animals[species]]

    def get_all_age(self, species) -> list:
        """
        Return the age of all animals in the cell by species
        """
        animals = {'herbivores': self.herbivores, 'carnivores': self.carnivores}
        return [animal.age for animal in animals[species]]
