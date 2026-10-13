from inseeds.components import base


class Component(base.Component):
    """Model mixing class for farmer_management.
    This component initializes farmers in the model to make decisions
    on which management practices to apply to their fields.
    Two practices are available: conventional and conservation tillage.
    The theory of planned behaviour is used to model farmer decision-making.
    Two farmer AFTs are implemented, the traditionalist and the pioneer.
    """
    # TODO: muss geändert werden
    def init_market(self, market_class, **kwargs):
        """Initialize farmers."""
        farmers = []

        for cell in self.world.cells:
            if cell.output.cftfrac.sum("band") == 0:
                continue

            farmer = farmer_class(cell=cell, model=self)
            farmers.append(farmer)

        farmers_sorted = sorted(farmers, key=lambda farmer: farmer.avg_hdate)
        for farmer in farmers_sorted:
            farmer.init_neighbourhood()

        # self.world.farmers = set(farmers_sorted

    def update(self, t):
        super().update(t)

        farmers_sorted = sorted(
            self.world.farmers, key=lambda farmer: farmer.avg_hdate
        )
        for farmer in farmers_sorted:
            farmer.update(t)