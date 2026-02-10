"""The inseeds_farmer.region class."""


class Region:
    """Region entity type mixin class."""

    def __init__(self, **kwargs):
        """Initialize an instance of Region."""
        super().__init__(**kwargs)


class Country(Region):
    """Country entity type mixin class."""

    def __init__(self, **kwargs):
        """Initialize an instance of Country."""
        super().__init__(**kwargs)

    @property
    def farmers(self):
        """Return farmers from this country's cells.

        Uses SocialSystem.individuals from lpjml.Country.
        """
        farmers = {
            farmer
            for farmer in self.individuals
            if farmer.__class__.__name__ == "Farmer"
        }
        return farmers

    def update(self, t):
        """Update country and its farmers."""
        super().update(t)

        farmers_sorted = sorted(
            self.farmers, key=lambda farmer: farmer.avg_hdate
        )

        for farmer in farmers_sorted:
            farmer.update(t)
