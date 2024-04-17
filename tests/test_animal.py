from scipy.stats import binom_test

from biosim.animals.herbivore import Herbivore
from biosim.animals.carnivore import Carnivore
import math
import pytest
import numpy as np
import scipy.stats as stats
from default_params import set_default_params


@pytest.fixture(autouse=True)
def reset_parameters():
    set_default_params()
    yield
    set_default_params()


@pytest.mark.parametrize('animal', [Herbivore(1, 10), Carnivore(1, 10)])
class TestAnimal:
    """
    Set of tests that apply equally to herbivore and carnivore
    """

    def test_aging(self, animal):
        """Test animals aging"""
        current_age = animal.age
        animal.aging()
        assert animal.age == current_age + 1

    def test_doesnt_give_birth(self, animal):
        """
        Test when animals cannot give birth
        High gamma, xi and zeta prevents birth
        """
        num_animals = 2
        animal.set_params({'gamma': 10, 'xi': 10, 'zeta': 10})
        child = animal.give_birth(num_animals)
        assert child is None

    def test_doesnt_give_birth_low_zeta(self, animal):
        """
        Test if animals cannot give birth with high gamma and xi, and low zeta
        """
        num_animals = 2
        animal.set_params({'gamma': 10, 'xi': 10, 'zeta': 0.1})
        child = animal.give_birth(num_animals)
        assert child is None

    def test_death_definite(self, animal):
        """
        Test if animals die when death is definite
        High omega ensures death"""
        animal.set_params({'omega': 100})
        assert animal.death()

    def test_set_params(self, animal):
        """Test setting parameters"""
        animal.set_params({"w_birth": 10.0})
        assert animal.w_birth == 10.0

    def test_invalid_params(self, animal):
        """Testing if unknown parameters not allowed"""
        with pytest.raises(ValueError):
            animal.set_params({"alpha": 5})

    def test_reset_fitness(self, animal):
        """Test reset fitness"""
        assert animal._fitness != 1
        animal.reset_fitness()
        assert animal._fitness == -1

    def test_lose_weight(self, animal):
        """
        Test if animal lose weight
        New weight is calculated reducing weight by Eta*Weight
        """
        new_weight = animal.weight - animal.eta * animal.weight
        animal.lose_weight()
        assert animal.weight == new_weight


@pytest.fixture()
def herbivore():
    return Herbivore(age=1, weight=10)


@pytest.mark.parametrize('animal', [Herbivore, Carnivore])
class TestAnimalNoObjectParameter:

    @pytest.fixture(autouse=True)
    def _init__(self, animal):
        self.animal = animal

    def test_empty_animal(self):
        """Empty animals can be created"""
        self.animal()

    def test_simple_animals(self):
        """Animals with parameters"""
        self.animal(age=5, weight=100)

    def test_animals_age(self):
        """Test negative age value"""
        with pytest.raises(ValueError):
            self.animal(age=-1)

    def test_animal_weight(self):
        """Test negative weight value"""
        with pytest.raises(ValueError):
            self.animal(weight=-1)

    def test_fitness_range(self):
        """Test fitness between 0 and 1"""
        for _ in range(100):
            assert 0 <= self.animal().fitness <= 1

    def test_animal_weight_zero(self):
        """Test zero weight"""
        h = self.animal(age=1, weight=0)
        assert h.weight == 0

    def test_fitness_zero_weight(self):
        """Test fitness for zero weight"""
        h = self.animal(age=1, weight=0)
        assert h.fitness == 0

    def test_animal_weight_not_zero(self):
        """Test if the weight is greater than zero"""
        self.animal.set_params({"w_birth": 10.0, "sigma_birth": 0.5})
        h = self.animal()
        assert h.weight > 0

    def test_animal_weight_none_stat(self):
        """When weight is not provided, check if weight gets set with a true mean of 6"""
        num_animals = 100
        animals = [self.animal() for _ in range(num_animals)]
        animal_weights = []
        for animal in animals:
            animal_weights.append(animal.weight)
        # Tow-sided Z-test with a 0.99 confidence level
        mu0 = self.animal.w_birth
        alpha = 0.01
        mean = np.mean(animal_weights)
        sd = np.std(animal_weights)
        Z_herb = (mean - mu0) / sd
        phi = 2 * stats.norm.cdf(-abs(Z_herb))
        assert phi > alpha

    def test_give_birth(self):
        """
        Test mother giving birth
        High weight and gamma ensure birth
        """
        mother_weight = 43
        h = self.animal(age=1, weight=mother_weight)
        num_animals = 2
        h.set_params({'gamma': 10})
        child = h.give_birth(num_animals)
        assert child.weight > 0
        assert child.age == 0
        assert h.weight == mother_weight - self.animal.xi * child.weight

    def test_migrate(self):
        """Test that a high mu and high fitness ensure migration"""
        self.animal.set_params({'mu': 2})
        h = self.animal(1, 40)
        assert h.migrate()

    def test_not_migrate(self):
        """
        Test that a low mu and low fitness prevent migration
        Set high age for low fitness.
        """
        self.animal.set_params({'mu': 0.1})
        h = self.animal(100, 10)
        assert not h.migrate()


def test_fitness(herbivore):
    """
    Test fitness of animal
    0.5 is obtained using formula 3 and 4 in the instructions. Calculated by Kristoffer Hemm.
    """
    calculated = 1 / (1 + math.exp(0.6 * (1 - 40))) * 1 / (1 + math.exp(-0.1 * (10 - 10)))
    assert herbivore.fitness == pytest.approx(calculated)


def test_feeding(herbivore):
    """
    Test feeding and weight increase.
    Weight increase calculated by formula Beta*Fodder
    """
    herbivore.feeding(Herbivore.F)
    assert herbivore.weight == 19


def test_reset_params_herbivore():
    """Test resetting parameters"""
    Herbivore.set_params({"w_birth": 10.0})
    h1 = Herbivore()
    assert h1.w_birth == 10.0
    Herbivore.reset_params()
    h2 = Herbivore()
    assert h2.w_birth == 8.0


def test_reset_params_carnivore():
    """Test resetting parameters"""
    Carnivore.set_params({"w_birth": 20.0})
    c1 = Carnivore()
    assert c1.w_birth == 20.0
    Carnivore.reset_params()
    h = Carnivore()
    assert h.w_birth == 6.0


@pytest.mark.parametrize("age, weight, is_dead", [(1, 0, True), (20, 0, True), (1, 10, False)])
def test_death(age, weight, is_dead):
    """Test death when weight and omega == 0"""
    Herbivore.set_params({'omega': 0})
    h = Herbivore(age=age, weight=weight)
    assert h.death() == is_dead


def test_full_carnivore_will_not_eat():
    """Test if one full carnivore will not eat a herbivore"""
    Carnivore.set_params({'F': 0})
    herbivore = [Herbivore(1, 10)]
    carnivore = Carnivore(2, 20)
    carnivore.eat_herbivores(herbivore)
    assert not herbivore[0].is_dead


def test_low_fitness_carnivore_cannot_eat_high_fitness_herbivore():
    """Test low fitness carnivore cannot eat high fitness herbivore"""
    Carnivore.reset_params()
    Herbivore.reset_params()
    herbivore = [Herbivore(5, 50)]
    carnivore = Carnivore(1, 10)
    carnivore.eat_herbivores(herbivore)
    assert not herbivore[0].is_dead


def test_not_migrate():
    """Test that a low mu and low fitness prevent migration"""
    Herbivore.set_params({'mu': 0.1})
    h = Herbivore(1, 10)
    assert not h.migrate()


def test_carnivore_will_eat_deltaphimax_high(mocker):
    """
    Test if one full carnivore will not eat a herbivore
    - Set Carnivore's DeltaPhiMax to 1 to pass Phi_carn-Phi_herb < DeltaPhiMax condition
    - Set Herbivore F to zero to prevent eating and gaining fitness
    """
    Carnivore.reset_params()
    Herbivore.reset_params()
    Carnivore.set_params({"DeltaPhiMax": 1, "gamma": 0.000001})
    Herbivore.set_params({"F": 0})
    herbivore = [Herbivore(1, 10)]
    carnivore = Carnivore(2, 20)
    # Set random.random = 0 to ensure kill
    mocker.patch('random.random', return_value=0)
    carnivore.eat_herbivores(herbivore)
    assert herbivore[0].is_dead


def test_carnivore_will_eat():
    """
    Test if one full carnivore will not eat a herbivore
    - Set Carnivore's DeltaPhiMax to 0 to not pass Phi_carn-Phi_herb < DeltaPhiMax condition
    - Set Herbivore F to zero to prevent eating and gaining fitness
    """
    Carnivore.reset_params()
    Herbivore.reset_params()
    Carnivore.set_params({"DeltaPhiMax": 0, "gamma": 0.000001})
    Herbivore.set_params({"F": 0})
    herbivore = [Herbivore(1, 10)]
    carnivore = Carnivore(2, 20)
    carnivore.eat_herbivores(herbivore)
    assert herbivore[0].is_dead


# Test with omega set to 0.1, 0.5 and 0.9
@pytest.mark.parametrize('omega', [0.1, 0.5, 0.9])
def test_death_binom(omega):
    # Acceptance for binomial test set 0.001
    alpha = 0.001
    Herbivore.set_params({'omega': omega})
    Carnivore.set_params({'omega': omega})
    herb = Herbivore(age=1, weight=10)
    carn = Carnivore(age=1, weight=2)
    herb_death_prob = omega * (1 - herb.fitness)
    carn_death_prob = omega * (1 - carn.fitness)
    n = 100
    herb_die_results = sum([herb.death() for _ in range(n)])
    carn_die_results = sum([carn.death() for _ in range(n)])
    pass_herbivores = binom_test(herb_die_results, n, herb_death_prob) < alpha
    pass_carnivores = binom_test(carn_die_results, n, carn_death_prob) < alpha
    assert pass_herbivores == pass_carnivores
