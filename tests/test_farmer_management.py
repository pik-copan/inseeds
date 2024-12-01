import os
import pytest
import pickle

import pycopanlpjml as lpjml

import inseeds.components.base as base
import inseeds.components.farming as farming
from inseeds.models.regenerative_tillage import Cell, Farmer, World


class Model(lpjml.Component, farming.Component):
    """Test class representing the model."""

    name = "Test InSEEDS farmer mananagement"
    description = "Subcomponent of the InSEEDS model representing only social \
    dynamics and decision-making on the basis of the TPB"

    def __init__(self, test_path, **kwargs):
        """Initialize an instance of World."""
        # Initialize the parent classes first
        super().__init__(**kwargs)

        # Ensure self.lpjml is initialized before accessing it
        if not hasattr(self, "lpjml") or self.lpjml is None:
            raise ValueError("lpjml must be initialized in the parent class.")

        with open(f"{test_path}/data/lpjml_input.pkl", "rb") as inp:
            lpjml_input = pickle.load(inp)

        with open(f"{test_path}/data/lpjml_output.pkl", "rb") as out:
            lpjml_output = pickle.load(out)

        # initialize LPJmL world
        self.world = World(
            model=self,
            input=lpjml_input,
            output=lpjml_output,
            grid=self.lpjml.grid,
            country=self.lpjml.country,
            area=self.lpjml.terr_area,
        )

        # initialize cells
        self.init_cells(cell_class=Cell)

        # initialize farmers
        self.init_farmers(farmer_class=Farmer)

    def update(self, t):
        super().update(t)

        self.update_lpjml(t)


def test_run_model(test_path):
    """Test the LPJmLCoupler class."""

    with open(f"{test_path}/data/lpjml.pkl", "rb") as lpj:
        lpjml = pickle.load(lpj)

    model = Model(lpjml=lpjml, test_path=test_path)

    for year in model.lpjml.get_sim_years():
        model.update(year)

    last_year = (
        model.world.output.time.values[0].astype("datetime64[Y]").astype(int).item()
        + 1970
    )

    # last year set to 2030 in test data set
    assert last_year == 2030
