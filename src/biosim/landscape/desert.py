from .baseland import Baseland
from ..animals.carnivore import Carnivore
from ..animals.herbivore import Herbivore
from typing import List


class Desert(Baseland):
    """
    Is habitable.
    Has no fodder for Herbivores.
    Carnivores can still feed on Herbivores.
    """
    # Parameters
    f_max = 0
    default_params = {"f_max": f_max}

    def __init__(self, herbivores: List[Herbivore] = None, carnivores: List[Carnivore] = None):
        super().__init__(herbivores=herbivores, carnivores=carnivores)
        self.landtype = "desert"
