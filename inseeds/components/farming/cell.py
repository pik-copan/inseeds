"""The inseeds_farmer.cell class."""

import inseeds.components.base as base


class Cell(base.Cell):
    """World entity type mixin class."""

    def __init__(self, **kwargs):
        """Initialize an instance of World."""
        super().__init__(**kwargs)

    # @property
    # def farmers(self):
    #     """Return the set of all farmers."""
    #     farmers = {
    #         farmer
    #         for farmer in self.individuals
    #         if farmer.__class__.__name__ == "Farmer"  # noqa
    #     }
    #     return farmers

    # @property
    # def farmer(self):
    #     """Return the first farmer."""
    #     farmers = self.farmers
    #     if len(farmers) == 0:
    #         return None
    #     return list(farmers)[0]
