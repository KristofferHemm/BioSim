from biosim.animals.herbivore import Herbivore
from biosim.animals.carnivore import Carnivore
from biosim.landscape.water import Water
from biosim.landscape.lowland import Lowland
from biosim.landscape.highland import Highland
from biosim.landscape.desert import Desert

herbivore_parameters = {"w_birth": 8.0,
                        "sigma_birth": 1.5,
                        "beta": 0.9,
                        "eta": 0.05,
                        "a_half": 40.0,
                        "phi_age": 0.6,
                        "w_half": 10.0,
                        "phi_weight": 0.1,
                        "mu": 0.25,
                        "gamma": 0.2,
                        "zeta": 3.5,
                        "xi": 1.2,
                        "omega": 0.4,
                        "F": 10.0}

carnivore_parameters = {"w_birth": 6.0,
                        "sigma_birth": 1.0,
                        "beta": 0.75,
                        "eta": 0.125,
                        "a_half": 40.0,
                        "phi_age": 0.3,
                        "w_half": 4.0,
                        "phi_weight": 0.4,
                        "mu": 0.4,
                        "gamma": 0.8,
                        "zeta": 3.5,
                        "xi": 1.1,
                        "omega": 0.8,
                        "F": 50.0,
                        "DeltaPhiMax": 10.0}
water_parameters = {"f_max": 0}
lowland_parameters = {"f_max": 800}
highland_parameters = {"f_max": 300}
desert_parameters = {"f_max": 0}


def set_default_params():
    Herbivore.set_params(herbivore_parameters)
    Carnivore.set_params(carnivore_parameters)
    Water.set_params(water_parameters)
    Lowland.set_params(lowland_parameters)
    Highland.set_params(highland_parameters)
    Desert.set_params(desert_parameters)
