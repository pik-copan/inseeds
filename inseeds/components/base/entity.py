import pandas as pd
from . import Output


class Entity:
    """Define properties.
    Inherits from I.World as the interface with all necessary variables
    and parameters.
    """

    output_variables = Output()

    def __init__(self, model=None):
        """Initialize an instance of World."""
        self.model = model

    @property
    def output_table(self):
        variables = self.__class__.output_variables.names
        if not variables:
            return pd.DataFrame()
        else:
            return pd.DataFrame(
                {
                    "year": [self.model.lpjml.sim_year] * len(variables),
                    "entity": [self.__class__.__name__] * len(variables),
                    "variable": [
                        getattr(
                            getattr(self.__class__.output_variables, var, None),
                            "name",
                            None,
                        )
                        for var in variables
                    ],
                    "value": [getattr(self, var, None) for var in variables],
                    "unit": [
                        getattr(
                            getattr(
                                getattr(self.__class__.output_variables, var, None),
                                "unit",
                                None,
                            ),
                            "symbol",
                            None,
                        )
                        for var in variables
                    ],
                }
            )

    def update(self, t):
        pass