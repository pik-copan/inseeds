"""Farmer entity type class of inseeds_farmer_management"""

# This file is part of pycopancore.
#
# Copyright (C) 2016-2017 by COPAN team at Potsdam Institute for Climate
# Impact Research
#
# URL: <http://www.pik-potsdam.de/copan/software>
# Contact: core@pik-potsdam.de
# License: BSD 2-clause license
import numpy as np

import pycopancore.model_components.base as core
import inseeds.components.base as base

# TODO
class Market(core.Individual, base.Individual):
    """Farmer (Individual) entity type mixin class."""

    # standard methods:
    def __init__(self, **kwargs):
        """Initialize an instance of Farmer."""
        super().__init__(**kwargs)  # must be the first line

        # initialize the Market specific attributes # TO-DO


        # average harvest date of the cell is used as a proxy for the order
        # of the agents making decisions in time through the year
        # self.avg_hdate = self.cell_avg_hdate # Zeitpunkt pro Jahr um Harvest zu verkaufen

        # soilc is the last "measured" soilc value of the farmer whereas the
        #   cell_soilc value is the actual status of soilc of the cell
        # self.soilc = self.cell_soilc

    #def init_neighbourhood(self):
    #    """Initialize the neighbourhood of the agent."""
    #    self.neighbourhood = [
    #        neighbour
    #        for cell_neighbours in self.cell.neighbourhood
    #        if len(cell_neighbours.individuals) > 0
    #        for neighbour in cell_neighbours.individuals
    #    ]

    @property
    # TODO: Abfrage ob Selbst auf Zelle oder Selbst auf Country
    def farmers(self):
        """Return the set of all farmers."""
        farmers = {
            farmer
            for farmer in self.cell.individuals
            if farmer.__class__.__name__ == "Farmer"  # noqa
        }
        return farmers

    @property
    def farmer(self):
        """Return the first farmer."""
        farmers = self.farmers
        if len(farmers) == 0:
            return None
        return list(farmers)[0]

    # TODO: Füll update function 
    def update(self, t):
        super().update(t)

        if self.control_run:
            return
