from .baseland import Baseland
from ..animals.carnivore import Carnivore
from ..animals.herbivore import Herbivore
from typing import List


class Highland(Baseland):
    """
    Is habitable.
    Has lower fodder count compared to Lowland.
    """
    # Parameters
    f_max = 300
    default_params = {"f_max": f_max}

    def __init__(self, herbivores: List[Herbivore] = None, carnivores: List[Carnivore] = None):
        super().__init__(herbivores=herbivores, carnivores=carnivores)
        self.landtype = "highland"
