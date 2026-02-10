"""The inseeds_farmer_mnagement.world class."""

import inseeds.components.base as base


class World(base.World):
    """World entity type mixin class."""

    def __init__(self, **kwargs):
        """Initialize an instance of World."""
        super().__init__(**kwargs)

    @property
    def farmers(self):
        """Return the set of all farmers."""
        farmers = {
            farmer
            for farmer in self.individuals
            if farmer.__class__.__name__ == "Farmer"  # noqa
        }
        return farmers

    def update(self, t):
        """Update all farmers (for models without countries)."""
        super().update(t)

        # Update farmers sorted by harvest date
        farmers_sorted = sorted(
            self.farmers, key=lambda farmer: farmer.avg_hdate
        )
        for farmer in farmers_sorted:
            farmer.update(t)
