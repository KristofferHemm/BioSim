from .animal import Animal


class Herbivore(Animal):
    """
    Herbivore class. Feeds on fodder on the island.
    """
    # Parameters
    w_birth = 8.0
    sigma_birth = 1.5
    beta = 0.9
    eta = 0.05
    a_half = 40.0
    phi_age = 0.6
    w_half = 10.0
    phi_weight = 0.1
    mu = 0.25
    gamma = 0.2
    zeta = 3.5
    xi = 1.2
    omega = 0.4
    F = 10.0

    default_params = {"w_birth": w_birth,
                      "sigma_birth": sigma_birth,
                      "beta": beta,
                      "eta": eta,
                      "a_half": a_half,
                      "phi_age": phi_age,
                      "w_half": w_half,
                      "phi_weight": phi_weight,
                      "mu": mu,
                      "gamma": gamma,
                      "zeta": zeta,
                      "xi": xi,
                      "omega": omega,
                      "F": F}
    weight_check_prob = zeta * (w_birth + sigma_birth)

    def __init__(self, age: int = 0, weight: float = None):
        super().__init__(age=age, weight=weight)
        self.species = "herbivore"
