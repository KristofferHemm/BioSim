from biosim.landscape.lowland import Lowland
from biosim.landscape.highland import Highland
from biosim.landscape.desert import Desert
from biosim.landscape.water import Water
from biosim.animals.herbivore import Herbivore
from biosim.animals.carnivore import Carnivore
from biosim.custom_exceptions import IllegalActionError
from default_params import set_default_params

import pytest


@pytest.fixture(autouse=True)
def reset_parameters():
    set_default_params()
    yield
    set_default_params()


@pytest.mark.parametrize('land', [Lowland, Highland])
class TestLand:
    """Set of tests that apply to both lowland and highland"""

    def test_set_params(self, land):
        """Test that parameters can be set"""
        land.set_params({"f_max": 10.0})
        assert land.f_max == 10.0

    def test_invalid_params(self, land):
        """Invalid parameters should throw errors"""
        with pytest.raises(ValueError):
            land.set_params({"alpha": 5})

    def test_feed_one_herbivore_all_fodder_consumed(self, land):
        """Feeding should remove all fodder if Herbivore.F>fodder"""
        f_max = 9
        land.set_params({"f_max": f_max})
        Herbivore.set_params({"F": 10})
        # Create lowland with 1 herbivore
        land = land([Herbivore()])
        land.feed()
        assert land.fodder == 0.0

    def test_num_animals(self, land):
        """Test the num_animals and num_animals_per_species property"""
        num_herb = 10
        num_carn = 20
        land = land([Herbivore() for _ in range(num_herb)], [Carnivore() for _ in range(num_carn)])
        assert land.num_animals == num_herb + num_carn
        assert land.num_animals_per_species == {"Herbivore": num_herb,
                                                "Carnivore": num_carn}

    def test_feed_one_carnivore_increase_weight(self, land):
        """
        Feeding should increase weight of carnivore
        - Set land f_max zero to prevent if from eating and gaining fitness
        - Set Carnivore's DeltaPhiMax to 0 to ensure it eating.
        """
        land.set_params({'f_max': 0})
        Carnivore.set_params({'DeltaPhiMax': 0})
        herbivore = Herbivore(1, 10)
        carnivore = Carnivore(2, 10)
        land = land([herbivore], [carnivore])
        c_weight = carnivore.weight
        land.feed()
        new_wt = c_weight + Carnivore.beta * herbivore.weight
        assert carnivore.weight == new_wt

    def test_birth_single_animal(self, land):
        """If there is a single animal there should be no birth"""
        land = land([Herbivore()])
        land.birth()
        assert land.num_animals == 1

    def test_step_num_animals(self, land):
        """
        Test number of animals after step
        - Set Carnivore's DeltaPhiMax to 0 to ensure it eating.
        - Set gamma to 0.000001 to prevent birth
        - Set Herbivore F to zero to prevent eating and gaining fitness
        Expecting herbivore to be eaten
        """
        Carnivore.set_params({"DeltaPhiMax": 0, "gamma": 0.000001})
        Herbivore.set_params({"F": 0})
        land = land([Herbivore(2, 20)],
                    [Carnivore(3, 30),
                     Carnivore(4, 40)])
        land.feed()
        assert land.num_animals == 2
        assert land.num_animals_per_species == {'Herbivore': 0, 'Carnivore': 2}

    def test_add_animal(self, land):
        """Test if adding one animal of each type to empty cell gives one animal of each type"""
        land = land()
        land.add_animal({'species': 'Herbivore', 'age': 1, 'weight': 10.})
        land.add_animal({'species': 'Carnivore', 'age': 1, 'weight': 10.})
        assert len(land.herbivores) == 1
        assert len(land.carnivores) == 1

    def test_add_animal_error(self, land):
        """Test if placing an illegal animal to empty cell raises error"""
        land = land()
        with pytest.raises(ValueError):
            land.add_animal({'species': 'Omnivore', 'age': 1, 'weight': 10.})

    def test_remove_herbivore_then_carnivore(self, land):
        """Test if a herbivore is correctly removed"""
        h = Herbivore()
        c = Carnivore()
        land = land([h], [c])
        land.remove_animal(h)
        assert len(land.herbivores) == 0
        land.remove_animal(c)
        assert len(land.carnivores) == 0

    def test_birth_multiple_animals_no_birth(self, land, mocker):
        """
        If there are multiple animals, test for births
        Two herbivores with low weight should give no births
        """
        herbivore1, herbivore2 = Herbivore(1, 10), Herbivore(2, 20)
        land = land([herbivore1, herbivore2])
        # Set random.random = 0 to allow for births
        mocker.patch('random.random', return_value=0)
        land.birth()
        assert len(land.herbivores) == 2

    def test_birth_two_herbivores_two_births(self, land):
        """
        Two herbivores with high weight and gamma, and low zeta and xi should give two births
        """
        Herbivore.set_params({'gamma': 10, 'zeta': 0.01, 'xi': 0.01})
        herbivore1, herbivore2 = Herbivore(1, 40), Herbivore(2, 40)
        land = land([herbivore1, herbivore2])
        land.birth()
        assert len(land.herbivores) == 4

    def test_birth_two_carnivores_two_births(self, land):
        """
        Two carnivores with high weight and gamma, and low zeta and xi should give two births
        """
        Carnivore.set_params({'gamma': 10, 'zeta': 0.01, 'xi': 0.01})
        carnivore1, carnivore2 = Carnivore(1, 40), Carnivore(2, 40)
        land = land([], [carnivore1, carnivore2])
        land.birth()
        assert land.num_carnivores == 4

    def test_birth_no_cross_specie_birth(self, land):
        """
        If there are multiple animals, test for births
        One herbivore and one carnivore with high weights should not give birth
        Set high weight and gamma, and low zeta and xi which should give birth
        """
        Herbivore.set_params({'gamma': 10, 'zeta': 0.01, 'xi': 0.01})
        Carnivore.set_params({'gamma': 10, 'zeta': 0.01, 'xi': 0.01})
        herbivore, carnivore = Herbivore(1, 40), Carnivore(2, 40)
        land = land([herbivore], [carnivore])
        land.birth()
        assert land.num_animals == 2

    def test_aging(self, land):
        """
        Test that the animals age
        """
        land = land([Herbivore(1, 10)])
        land.aging()
        assert land.herbivores[0].age == 2

    def test_lose_weight(self, land):
        """
        Test that the animals lose weight
        """
        herbivore = Herbivore(1, 10)
        h_weight = herbivore.weight
        land = land([herbivore])
        new_wt = h_weight - herbivore.eta * herbivore.weight
        land.lose_weight()
        assert new_wt == land.herbivores[0].weight

    def test_death_none(self, land):
        """
        Test that no animal die with low omega and high weight
        """
        Herbivore.set_params({'omega': 0.001})
        Carnivore.set_params({'omega': 0.001})
        land = land([Herbivore(1, 40)],
                    [Carnivore(1, 40)])
        land.die()
        assert len(land.herbivores) == 1
        assert len(land.carnivores) == 1

    def test_deaths_all(self, land):
        """
        Test if all animals die with high omega and low weight
        """
        Herbivore.set_params({'omega': 100})
        Carnivore.set_params({'omega': 100})
        land = land([Herbivore(1, 10)],
                    [Carnivore(1, 10)])
        land.die()
        assert len(land.herbivores) == 0
        assert len(land.carnivores) == 0

    def test_get_migration(self, land, mocker):
        """Test if animal will migrate if µΦ > randint"""
        land = land([Herbivore()])
        mocker.patch('random.random', return_value=0)
        assert len(land.get_migrations()) == 1

    def test_no_migration(self, land, mocker):
        """Test if no animal will migrate if µΦ < randint"""
        land = land([Herbivore()])
        mocker.patch('random.random', return_value=1)
        assert len(land.get_migrations()) == 0

    def test_get_all_fitness(self, land):
        """Test if fitness is returned for all animals"""
        num_herb = 10
        num_carn = 20
        land = land([Herbivore() for _ in range(num_herb)], [Carnivore() for _ in range(num_carn)])
        herb_fitness = land.get_all_fitness('herbivores')
        carn_fitness = land.get_all_fitness('carnivores')
        assert len(herb_fitness) == num_herb
        assert len(carn_fitness) == num_carn

    def test_get_all_weight(self, land):
        """Test if fitness is returned for all animals"""
        num_herb = 10
        num_carn = 20
        land = land([Herbivore() for _ in range(num_herb)], [Carnivore() for _ in range(num_carn)])
        herb_weight = land.get_all_weight('herbivores')
        carn_weight = land.get_all_weight('carnivores')
        assert len(herb_weight) == num_herb
        assert len(carn_weight) == num_carn

    def test_get_all_age(self, land):
        """Test if age is returned for all animals"""
        num_herb = 10
        num_carn = 20
        land = land([Herbivore() for _ in range(num_herb)], [Carnivore() for _ in range(num_carn)])
        herb_age = land.get_all_age('herbivores')
        carn_age = land.get_all_age('carnivores')
        assert len(herb_age) == num_herb
        assert len(carn_age) == num_carn


class TestLowland:
    """Tests dependent on fodder run on lowland only"""

    # parametrize for all island types
    def test_reset_params(self):
        """Parameters should be reset to default values"""
        Lowland.set_params({"f_max": 10.0})
        Lowland.reset_params()
        h = Lowland()
        assert h.f_max == 800

    def test_feed_one_herbivore_reduce_fodder(self):
        """Feeding should reduce fodder"""
        f_max = 800
        Lowland.set_params({"f_max": f_max})
        # Create lowland with 1 herbivore
        lowland = Lowland([Herbivore()])
        lowland.feed()
        assert lowland.fodder == f_max - Herbivore.F

    def test_feed_one_herbivore_weight(self):
        """Feeding should increase weight of herbivore"""
        f_max = 800
        Lowland.set_params({"f_max": f_max})
        herbivore = Herbivore()
        h_weight = herbivore.weight
        lowland = Lowland([herbivore])
        lowland.feed()
        new_wt = h_weight + Herbivore.beta * Herbivore.F
        assert herbivore.weight == new_wt

    def test_feed_carnivore_appetite_full_fail(self):
        """Carnivore should not eat herbivore with zero appetite.
        - Set Carnivore F to 0 to remove its appetite.
        - Set Carnivore DeltaPhiMax to 0 to increase eating probability.
        - Set Herbivore F to zero to prevent eating and gaining fitness
        """
        Carnivore.set_params({"DeltaPhiMax": 0, "F": 0})
        Herbivore.set_params({"F": 0})
        herbivore = Herbivore(1, 10)
        carnivore = Carnivore(2, 20)
        lowland = Lowland([herbivore], [carnivore])
        lowland.feed()
        assert len(lowland.herbivores) == 1

    def test_reset_fodder(self):
        """Test if fodder resets to 800"""
        lowland = Lowland()
        lowland.fodder = 10
        lowland.reset_fodder()
        assert lowland.f_max == 800

    def test_step(self, mocker):
        """
        Test the step method
        Should increase weight, as increase weight > reduce weight
        Should increase age by 1
        Should keep number of animals constant, no births or deaths
        """
        herbivore1, herbivore2 = Herbivore(1, 10), Herbivore(2, 20)
        lowland = Lowland([herbivore1, herbivore2])
        h_weight = herbivore1.weight
        # Make sure no animal dies
        mocker.patch('random.random', return_value=1)
        lowland.step()
        new_wt_feed = h_weight + herbivore1.beta * herbivore1.F
        new_wt_lose_weight = new_wt_feed - herbivore1.eta * new_wt_feed
        assert herbivore1.weight == new_wt_lose_weight
        assert herbivore1.age == 2
        assert lowland.num_animals == 2


class TestWater:
    """Tests that only apply to water"""

    def test_add_animal(self):
        """Test if adding one animal to water gives no animal"""
        water = Water()
        with pytest.raises(IllegalActionError):
            water.add_animal({'species': 'Herbivore', 'age': 1, 'weight': 10.})


class TestDesert:
    """Tests that only apply to desert"""

    def test_herbivore_cant_eat(self):
        """Test if one herbivore in desert will not eat"""
        # Create desert with 1 herbivore
        herbivore = Herbivore(1, 10)
        desert = Desert([herbivore])
        desert.feed()
        assert herbivore.weight == 10

    def test_carnivore_can_eat(self, mocker):
        """Test if one carnivore will eat a herbivore in desert"""
        # Create desert with 1 herbivore and 1 carnivore
        herbivore = Herbivore(1, 10)
        carnivore = Carnivore(2, 20)
        desert = Desert([herbivore], [carnivore])
        # Make sure that the carnivore successfully kills herbivore
        mocker.patch('random.random', return_value=0)
        desert.feed()
        assert len(desert.herbivores) == 0
