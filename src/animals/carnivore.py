import random

from .animal import Animal


class Carnivore(Animal):
    """
    Carnivore class. Capable of eating the Herbivore class.
    """
    # Parameters
    w_birth = 6.0
    sigma_birth = 1.0
    beta = 0.75
    eta = 0.125
    a_half = 40.0
    phi_age = 0.3
    w_half = 4.0
    phi_weight = 0.4
    mu = 0.4
    gamma = 0.8
    zeta = 3.5
    xi = 1.1
    omega = 0.8
    F = 50.0
    DeltaPhiMax = 10.0

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
                      "F": F,
                      "DeltaPhiMax": DeltaPhiMax}
    weight_check_prob = zeta * (w_birth + sigma_birth)

    def __init__(self, age: int = 0, weight: float = None):
        super().__init__(age=age, weight=weight)
        self.species = "carnivore"

    def eat_herbivores(self, herbivores):
        """
        Carnivores will kill herbivores with a probability of

        .. math::
            p = \\left\\{\\begin{matrix}
            0 & if \\  \\ \\Phi_{carn} \\leq \\Phi_{herb}\\\\
            \\frac{\\Phi_{carn}-\\Phi_{herb}}{\\Delta \\Phi_{max}} & if \\
              0 < \\Phi_{carn}-\\Phi_{herb} \\leq \\Delta \\Phi_{max}\\\\
            1 & otherwise
            \\end{matrix}\\right.

        """
        # Carnivores only eat until their appetite persists
        carn_appetite = self.F
        # Carnivore prays on each Herbivore until it's full
        # or all Herbivores have been attempted to be killed.
        for herb in herbivores:
            if carn_appetite <= 0:
                break
            # Calculate the probability of the Carnivore eating the Herbivore
            if self.fitness <= herb.fitness:
                # Herbivores are in ascending order of fitness,
                # If the carnivore cannot eat this herbivore, it
                # cannot eat subsequent herbivores.
                break
            elif 0 < self.fitness - herb.fitness < self.DeltaPhiMax:
                prob = (self.fitness - herb.fitness) / self.DeltaPhiMax
            else:
                prob = 1

            if prob == 1 or random.random() < prob:
                # Carnivore eats the herbivore
                # If the weight of the herbivore exceeds the amount of food desired
                # by the carnivore, the carnivore eats only the amount it wants.
                # The remainder of the herbivore goes to waste.
                eaten = self.feeding(min(carn_appetite, herb.weight))
                # Carnivore's appetite is decreased by the weight of the Herbivore
                carn_appetite -= eaten
                herb.is_dead = True
        return [herb for herb in herbivores if not herb.is_dead]
