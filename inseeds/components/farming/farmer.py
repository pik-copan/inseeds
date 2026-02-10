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
import time
from enum import Enum

import pycopancore.model_components.base as core
import inseeds.components.base as base


class AFT(Enum):
    """AFT types for the farmers."""

    traditionalist: int = 0
    pioneer: int = 1

    @staticmethod
    def random(pioneer_share=0.5):
        return np.random.choice(
            [AFT.pioneer, AFT.traditionalist],
            p=[pioneer_share, 1 - pioneer_share],
        )


class Farmer(core.Individual, base.Individual):
    """Farmer (Individual) entity type mixin class."""

    # standard methods:
    def __init__(self, **kwargs):
        """Initialize an instance of Farmer."""
        super().__init__(**kwargs)  # must be the first line

        # initialize the AFT specific attributes
        self.init_aft()

        # initialize the coupled (lpjml mapped) attributes
        self.init_coupled_attributes()

        # average harvest date of the cell is used as a proxy for the order
        # of the agents making decisions in time through the year
        self.avg_hdate = self.cell_avg_hdate

        # soilc is the last "measured" soilc value of the farmer whereas the
        #   cell_soilc value is the actual status of soilc of the cell
        self.soilc = self.cell_soilc

        # Same applies for cropyield (as for soilc)
        self.cropyield = self.cell_cropyield

    def init_aft(self):
        """Initialize the AFT of the agent."""

        # assign aft to farmer
        self.aft = AFT.random(self.model.config.coupled_config.pioneer_share)
        self.aft_id = self.aft.value

        # assign configuration to aft specific farmer
        self.__dict__.update(
            getattr(
                self.model.config.coupled_config.aftpar, self.aft.name
            ).to_dict()
        )

    def init_coupled_attributes(self):
        """Initialize the mapped variables from the LPJmL output to the
        farmers
        """

        # get the coupling map (inseeds to lpjml names) from the configuration
        self.coupling_map = (
            self.model.config.coupled_config.coupling_map.to_dict()
        )

        # set control run argument
        self.control_run = self.model.config.coupled_config.control_run

        # set the mapped variables from the farmers to the LPJmL input
        for attribute, lpjml_attribute in self.coupling_map.items():
            if not isinstance(lpjml_attribute, list):
                lpjml_attribute = [lpjml_attribute]

            for single_var in lpjml_attribute:
                input_data = self.cell.to_earth[single_var].values

                if len(input_data.flatten()) > 1:
                    continue
                setattr(self, attribute, input_data.item())

    def init_neighbourhood(self):
        """Initialize the neighbourhood of the agent."""
        self.neighbourhood = [
            neighbour
            for cell_neighbours in self.cell.neighbourhood
            if len(cell_neighbours.individuals) > 0
            for neighbour in cell_neighbours.individuals
        ]

    @property
    def cell_cropyield(self):
        """Return the average crop yield of the cell."""
        harvestc_data = self.cell.from_earth.harvestc.values
        if harvestc_data.mean() == 0:
            return 1e-3
        else:
            return harvestc_data.mean()

    @property
    def cell_soilc(self):
        """Return the average soil carbon of the cell."""
        top_soilc_data = self.cell.from_earth.soilc_agr_layer.isel(
            band=0
        ).item()
        if top_soilc_data == 0:
            return 1e-3
        else:
            return top_soilc_data

    @property
    def cell_avg_hdate(self):
        """Return the average harvest date of the cell."""
        hdate_data = self.cell.from_earth.hdate
        cftfrac_data = self.cell.from_earth.cftfrac

        # Get band values for both variables
        hdate_bands = hdate_data.band.values
        cftfrac_bands = cftfrac_data.band.values

        # Find crop indices in hdate bands that match cftmap
        hdate_crop_idx = [
            i
            for i, item in enumerate(hdate_bands)
            if any(x in item for x in self.model.config.cftmap)
        ]

        # Find matching bands in cftfrac (same crop names)
        hdate_crop_names = [hdate_bands[i] for i in hdate_crop_idx]
        cftfrac_crop_idx = [
            i
            for i, item in enumerate(cftfrac_bands)
            if item in hdate_crop_names
        ]

        if len(cftfrac_crop_idx) == 0:
            return 365

        # Get the selected data
        hdate_selected = hdate_data.isel(band=hdate_crop_idx)
        cftfrac_selected = cftfrac_data.isel(band=cftfrac_crop_idx)

        if np.sum(cftfrac_selected.values) == 0:
            return 365
        else:
            return np.average(
                hdate_selected.values, weights=cftfrac_selected.values
            )

    def set_lpjml(self, attribute):
        """Set the mapped variables from the farmers to the LPJmL input."""
        lpjml_attribute = self.coupling_map[attribute]

        if not isinstance(lpjml_attribute, list):
            lpjml_attribute = [lpjml_attribute]

        for single_var in lpjml_attribute:
            self.cell.to_earth[single_var][:] = getattr(self, attribute)

    def update(self, t):
        super().update(t)

        # update the average harvest date of the cell
        self.avg_hdate = self.cell_avg_hdate

        # running average over strategy_switch_duration years to avoid rapid
        #    switching by weather fluctuations
        self.cropyield = (
            (1 - 1 / self.strategy_switch_duration) * self.cropyield
            + 1 / self.strategy_switch_duration * self.cell_cropyield
        )
        self.soilc = (
            (1 - 1 / self.strategy_switch_duration) * self.soilc
            + 1 / self.strategy_switch_duration * self.cell_soilc
        )
