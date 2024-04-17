from biosim.animals.carnivore import Carnivore
from biosim.animals.herbivore import Herbivore
from biosim.custom_exceptions import IllegalActionError
from biosim.island import Island
from biosim.landscape.lowland import Lowland
from default_params import set_default_params

import random
import pytest
import numpy as np
import scipy.stats as stats


@pytest.fixture(autouse=True)
def reset_parameters():
    set_default_params()
    yield
    set_default_params()


class TestIsland:
    @pytest.fixture(autouse=True)
    def create_island(self):
        random.seed(1234)
        geography = "WWW\nWLW\nWWW"
        self.island = Island(geography)
        yield
        Herbivore.reset_params()
        Carnivore.reset_params()
        Lowland.reset_params()

    def test_island(self):
        """Test if an island is created correctly"""
        assert self.island.shape == (3, 3)
        assert self.island.island_map[(2, 2)].landtype == "lowland"
        assert self.island.island_map[(1, 1)].landtype == "water"

    def test_illegal_cell_types(self):
        """Test that illegal landtype is addressed"""
        geography = "WWW\nWXW\nWWW"
        with pytest.raises(ValueError):
            self.island = Island(geography)

    def test_illegal_map_shape(self):
        """Test that illegal island shape is addressed"""
        geography = "WWW\nWLLW\nWWW"
        with pytest.raises(ValueError):
            self.island = Island(geography)

    def test_illegal_map_top(self):
        """Test that placing non-water on the top edge is addressed"""
        geography = "WLW\nWLW\nWWW"
        with pytest.raises(ValueError):
            self.island = Island(geography)

    def test_illegal_map_bottom(self):
        """Test that placing non-water on the bottom edge is addressed"""
        geography = "WWW\nWLW\nWLW"
        with pytest.raises(ValueError):
            self.island = Island(geography)

    def test_illegal_map_left(self):
        """Test that placing non-water on the left edge is addressed"""
        geography = "WWW\nLLW\nWWW"
        with pytest.raises(ValueError):
            self.island = Island(geography)

    def test_illegal_map_right(self):
        """Test that placing non-water on the right edge is addressed"""
        geography = "WWW\nWLL\nWWW"
        with pytest.raises(ValueError):
            self.island = Island(geography)

    def test_place_animals(self):
        """Test that animals get placed with correct values"""
        x = [{'loc': (2, 2),
              'pop': [{'species': 'Herbivore', 'age': 1, 'weight': 10.},
                      {'species': 'Herbivore', 'age': 2, 'weight': 20.}]
              }]
        self.island.place_animals(x)
        assert self.island.island_map[(2, 2)].num_animals == 2
        assert self.island.island_map[(2, 2)].herbivores[0].age == 1
        assert self.island.island_map[(2, 2)].herbivores[0].weight == 10.
        assert self.island.island_map[(2, 2)].herbivores[1].age == 2
        assert self.island.island_map[(2, 2)].herbivores[1].weight == 20.

    def test_place_animals_on_water(self):
        """Placing animals in water raises value error"""
        x = [{'loc': (1, 1),
              'pop': [{'species': 'Herbivore', 'age': 1, 'weight': 10.},
                      {'species': 'Herbivore', 'age': 2, 'weight': 20.}]
              }]
        with pytest.raises(IllegalActionError):
            self.island.place_animals(x)

    def test_step_age(self):
        """
        Test if one step increases the age of animals
        Set a low omega so animals do not die
        """
        Herbivore.set_params({"omega": 0.001})
        x = [{'loc': (2, 2),
              'pop': [{'species': 'Herbivore', 'age': 1, 'weight': 10.},
                      {'species': 'Herbivore', 'age': 2, 'weight': 20.}]
              }]
        self.island.place_animals(x)
        self.island.step()
        assert self.island.island_map[(2, 2)].herbivores[0].age == 2
        assert self.island.island_map[(2, 2)].herbivores[1].age == 3

    def test_num_animals(self):
        """Test that the number of animals placed in a cell is correct"""
        geography = "WWW\nWLW\nWWW"
        self.island = Island(geography)
        x = [{'loc': (2, 2),
              'pop': [{'species': 'Herbivore',
                       'age': 5,
                       'weight': 20}
                      for _ in range(20)]}]
        self.island.place_animals(x)
        assert self.island.num_animals == 20

    def test_num_animals_per_species(self):
        """Test that the number of animals per specie placed in a cell are correct"""
        geography = "WWW\nWLW\nWWW"
        self.island = Island(geography)
        x = [{'loc': (2, 2),
              'pop': [{'species': 'Herbivore',
                       'age': 5,
                       'weight': 20}
                      for _ in range(20)]},
             {'loc': (2, 2),
              'pop': [{'species': 'Carnivore',
                       'age': 5,
                       'weight': 20}
                      for _ in range(10)]}]
        self.island.place_animals(x)
        assert self.island.num_animals_per_species['Herbivore'] == 20
        assert self.island.num_animals_per_species['Carnivore'] == 10

    def test_migration_four_directions(self):
        """Test if all animals move away from center cell in a one-step migration"""
        random.seed(1234)
        geography = "WWWWW\nWLLLW\nWLLLW\nWLLLW\nWWWWW"
        self.island = Island(geography)
        Herbivore.set_params({"mu": 100,
                              "a_half": 1000,
                              "w_half": 0.001})
        x = [{'loc': (3, 3),
              'pop': [{'species': 'Herbivore', 'age': 1, 'weight': 10.},
                      {'species': 'Herbivore', 'age': 2, 'weight': 20.},
                      {'species': 'Herbivore', 'age': 3, 'weight': 30.},
                      {'species': 'Herbivore', 'age': 4, 'weight': 40.}]
              }]
        self.island.place_animals(x)
        assert self.island.island_map[(3, 2)].num_animals == 0
        assert self.island.island_map[(3, 3)].num_animals == 4
        self.island.migrate()
        assert self.island.island_map[(3, 3)].num_animals == 0

    def test_migration_stat(self):
        """Test if 1/4 of all animals move in each direction: north, west, east, south
         for a one-step migration"""
        random.seed(1234)
        geography = "WWWWW\nWLLLW\nWLLLW\nWLLLW\nWWWWW"
        north, west, east, south = [], [], [], []
        # Simulate 100 migrations
        for sim in range(100):
            self.island = Island(geography)
            Herbivore.set_params({"mu": 100,
                                  "a_half": 1000,
                                  "w_half": 0.001})
            x = [{'loc': (3, 3),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(100)]}]
            self.island.place_animals(x)
            self.island.migrate()
            north.append(self.island.island_map[(2, 3)].num_animals)
            west.append(self.island.island_map[(3, 2)].num_animals)
            east.append(self.island.island_map[(3, 4)].num_animals)
            south.append(self.island.island_map[(4, 3)].num_animals)
        neighbors = [north, west, east, south]
        mu0 = 25
        alpha = 0.01
        # 2-sided Z-test with a 0.99 confidence level
        for neighbor in neighbors:
            mean = np.mean(neighbor)
            sd = np.std(neighbor)
            z = (mean - mu0) / sd
            phi = 2 * stats.norm.cdf(-abs(z))
            assert phi > alpha

    def test_get_current_population_stat(self):
        """Test get_current_population_state,fitness,weight,age"""
        geography = "WWWWW\nWLLLW\nWLLLW\nWLLLW\nWWWWW"
        self.island = Island(geography)
        Herbivore.set_params({"mu": 100,
                              "a_half": 1000,
                              "w_half": 0.001})
        x = [{'loc': (3, 3),
              'pop': [{'species': 'Herbivore', 'age': 1, 'weight': 10.},
                      {'species': 'Herbivore', 'age': 2, 'weight': 20.},
                      {'species': 'Herbivore', 'age': 3, 'weight': 30.},
                      {'species': 'Carnivore', 'age': 4, 'weight': 40.}]
              }]
        self.island.place_animals(x)
        assert self.island.get_current_herbivore_population_state()[2, 2] == 3
        assert self.island.get_current_carnivore_population_state()[2, 2] == 1
        assert len(self.island.get_current_herbivore_fitness()) == 3
        assert len(self.island.get_current_carnivore_fitness()) == 1
        assert len(self.island.get_current_herbivore_weight()) == 3
        assert len(self.island.get_current_carnivore_weight()) == 1
        assert len(self.island.get_current_herbivore_age()) == 3
        assert len(self.island.get_current_carnivore_age()) == 1
