import os
from biosim.simulation import BioSim
from biosim.animals.herbivore import Herbivore
from biosim.landscape.lowland import Lowland
from default_params import set_default_params

import pytest
import textwrap


@pytest.fixture(autouse=True)
def reset_parameters():
    set_default_params()
    yield
    set_default_params()


def test_step():
    """
    Test if one step will go correctly on a one cell island without death
    Age should increase by one
    Number of animals should increase
    Fodder should down
    Fitness should increase
    """
    geogr = """\
               WWW
               WLW
               WWW"""
    geogr = textwrap.dedent(geogr)
    # Set herbivore params to prevent death and ensure birth
    Herbivore.set_params({'gamma': 10000, 'xi': 0, 'zeta': 0, 'omega': 0.001})
    ini_herbs = [{'loc': (2, 2),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(50)]}]
    sim = BioSim(geogr, ini_herbs, seed=1, vis_years=0)
    ini_num_animals = sim.num_animals
    ini_fodder = sim.island.habitable_map[2, 2].fodder
    ini_fitness = sim.island.get_current_herbivore_fitness()[0]
    sim.simulate(1)
    assert sim.island.num_animals > ini_num_animals
    assert sim.island.get_current_herbivore_age()[0] == 6
    assert sim.island.get_current_herbivore_fitness()[0] > ini_fitness
    assert sim.island.habitable_map[2, 2].fodder < ini_fodder


def test_set_animal_parameters():
    geogr = """\
                   WWW
                   WLW
                   WWW"""
    geogr = textwrap.dedent(geogr)
    # Set herbivore params to prevent death and ensure birth
    Herbivore.set_params({'gamma': 2})
    assert Herbivore.gamma == 2
    ini_herbs = [{'loc': (2, 2),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(50)]}]
    sim = BioSim(geogr, ini_herbs, seed=1, vis_years=0)
    sim.set_animal_parameters('Herbivore', {'gamma': 1, 'xi': 0, 'zeta': 0})
    assert Herbivore.gamma == 1


def test_set_landscape_parameters():
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
    sim = BioSim(geogr, ini_herbs, seed=1, vis_years=0)
    assert Lowland.f_max == 800
    sim.set_landscape_parameters('L', {'f_max': 500})
    assert Lowland.f_max == 500


@pytest.fixture
def log_file():
    log_file_ = "logs.csv"
    yield log_file_
    os.remove(log_file_)


def test_log_file_saved(log_file):
    sim = BioSim(island_map="WWWW\nWLHW\nWWWW",
                 ini_pop=[],
                 seed=1,
                 vis_years=None,
                 log_file=log_file)
    sim.simulate(2)

    assert os.path.isfile(log_file)


@pytest.fixture
def log_file_state():
    log_file_ = "logs.csv"
    state_file_ = "logs.json"
    yield log_file_, state_file_
    os.remove(log_file_)
    os.remove(state_file_)


def test_simulation_state_saving(log_file_state):
    log_file = log_file_state[0]
    state_file = log_file_state[1]
    sim = BioSim(island_map="WWWW\nWLHW\nWWWW",
                 ini_pop=[{'loc': (2, 2),
                            'pop': [{'species': 'Herbivore',
                                     'age': 5,
                                     'weight': 20}
                                    for _ in range(50)]}],
                 seed=1,
                 vis_years=None,
                 log_file=log_file)
    sim.simulate(2)
    sim.save_state()
    # Test that csv and json files are created
    assert os.path.isfile(log_file)
    assert os.path.isfile(state_file)

    # load state
    sim2 = BioSim.load_state(log_file)
    # Test that the simulation resumes.
    sim2.simulate(2)
