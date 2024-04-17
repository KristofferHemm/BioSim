from .baseland import Baseland
from ..animals.carnivore import Carnivore
from ..animals.herbivore import Herbivore
from typing import List


class Lowland(Baseland):
    """
    Is habitable.
    Has high fodder count for Herbivores.
    """
    # Parameters
    f_max = 800
    default_params = {"f_max": f_max}

    def __init__(self, herbivores: List[Herbivore] = None, carnivores: List[Carnivore] = None):
        self.fodder = self.f_max
        super().__init__(herbivores=herbivores, carnivores=carnivores)
        self.landtype = "lowland"
