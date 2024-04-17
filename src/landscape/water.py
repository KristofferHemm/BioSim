from ..custom_exceptions import IllegalActionError
from .baseland import Baseland


class Water(Baseland):
    """
    Is uninhabitable.
    No animals can be placed.
    """
    # Parameters
    f_max = 0
    default_params = {"f_max": f_max}

    def __init__(self):
        super().__init__()
        self.is_habitable = False
        self.landtype = "water"

    def add_animal(self, animal):
        """
        Animals cannot be in water.
        """
        raise IllegalActionError("Animals cannot be placed on water")
