"""Farmer entity type class of inseeds_farmer_management"""

import numpy as np

from inseeds.components import farming


class Farmer(farming.Farmer):
    """Farmer (Individual) entity type mixin class."""

    def __init__(self, **kwargs):
        """Initialize an instance of Farmer."""
        super().__init__(**kwargs)  # must be the first line

        # initialize previous soilc
        self.soilc_previous = self.soilc

        # initialize previous cropyield
        self.cropyield_previous = self.cropyield

        # Randomize switch time at beginning of simulation to avoid
        #   synchronization of agents
        self.strategy_switch_time = np.random.randint(
            0, self.strategy_switch_duration
        )

        # initialize tbp for meaningful output
        self.tpb = 0

    @property
    def attitude(self):
        """Calculate the attitude of the farmer following the TPB"""
        return (
            self.weight_social_learning * self.attitude_social_learning
            + self.weight_own_land * self.attitude_own_land
        )

    @property
    def attitude_own_land(self):
        """Calculate the attitude of the farmer based on their own land"""
        # compare own soil and yield to previous values
        attitude_own_soil = self.soilc_previous / self.soilc - 1
        attitude_own_yield = self.cropyield_previous / self.cropyield - 1

        return sigmoid(
            self.weight_yield * attitude_own_yield
            + self.weight_soil * attitude_own_soil
        )

    @property
    def attitude_social_learning(self):
        """Calculate the attitude of the farmer through social learning based
        on the comparison to neighbours using a different strategy"""

        # split variables (crop yield, soilc) status of neighbours into groups
        #   of different strategies applied and average them
        average_cropyields = self.split_neighbourhood_status("cropyield")
        average_soilcs = self.split_neighbourhood_status("soilc")

        # select the average of the neighbours that are using a different
        #   strategy
        yields_diff = average_cropyields[not self.tillage]
        soils_diff = average_soilcs[not self.tillage]

        # calculate the difference between the own status and the average
        #   status of the neighbours
        if np.isnan(yields_diff):
            yield_comparison = 0
        else:
            yield_comparison = yields_diff / self.cropyield - 1

        if np.isnan(soils_diff):
            soil_comparison = 0
        else:
            soil_comparison = soils_diff / self.soilc - 1

        # calculate the attitude of social learning based on the comparison
        return sigmoid(
            self.weight_yield * yield_comparison
            + self.weight_soil * soil_comparison
        )

    @property
    def social_norm(self):
        """Calculate the social norm of the farmer based on the majority
        behaviour of the neighbours"""
        social_norm = 0
        if self.neighbourhood:
            social_norm = sum(n.tillage for n in self.neighbourhood) / len(
                self.neighbourhood
            )
        if self.tillage == 1:
            return sigmoid(0.5 - social_norm)
        else:
            return sigmoid(social_norm - 0.5)

    def split_neighbourhood(self, attribute):
        """split the neighbourhood of farmers after a defined boolean attribute
        (e.g. tillage)
        """
        # init split into two neighbourhood lists
        first_nb = []
        second_nb = []

        # split the neighbourhood into two groups based on the attribute
        #   of the neighbours
        for neighbour in self.neighbourhood:
            if getattr(neighbour, attribute) == 0:
                first_nb.append(neighbour)
            else:
                second_nb.append(neighbour)
        return first_nb, second_nb

    def split_neighbourhood_status(self, variable):
        """split the neighbourhood of farmers after a defined attribute
        (tillage) and calculate the average of each group
        """
        # split the neighbourhood into two groups based on the behaviour
        first_nb, second_nb = self.split_neighbourhood("tillage")

        # calculate the average of the variable for first group
        if first_nb:
            first_var = sum(getattr(n, variable) for n in first_nb) / len(
                first_nb
            )
        # if there are no neighbours of the same strategy, set the average
        #   to 0
        else:
            first_var = np.nan

        # calculate the average of the variable for second group
        if second_nb:
            second_var = sum(getattr(n, variable) for n in second_nb) / len(
                second_nb
            )
        # if there are no neighbours of the same strategy, set the average
        #   to 0
        else:
            second_var = np.nan

        return first_var, second_var

    def update(self, t):
        # call the base class update method
        super().update(t)

        """Update the behaviour of the farmer based on the TPB"""

        # If strategy switch time is down to 0 calculate TPB-based strategy
        # switch probability value
        if self.strategy_switch_time <= 0:
            self.tpb = (
                self.weight_attitude * self.attitude
                + self.weight_norm * self.social_norm
            ) * self.pbc

            if self.tpb > 0.5:
                # switch strategy
                self.tillage = int(not self.tillage)

                # decrease pbc after strategy switch
                self.pbc = max(self.pbc - 0.25, 0.5)

                # set back counter for strategy switch
                self.strategy_switch_time = np.random.normal(
                    self.strategy_switch_duration,
                    round(self.strategy_switch_duration / 2),
                )

                # freeze the current soilc and cropyield values that were used
                #   for the decision making in the next evaluation after
                #   self.strategy_switch_duration
                self.cropyield_previous = self.cropyield
                self.soilc_previous = self.soilc

                # set the values of the farmers attributes to the LPJmL
                #   variables
                self.set_lpjml(attribute="tillage")

            # increase pbc if tpb is near 0.5 to learn from own experience
            elif self.tpb <= 0.5 and self.tpb > 0.4:
                self.pbc = min(
                    self.pbc + 0.25 / self.strategy_switch_duration, 1
                )

        else:
            # decrease the counter for strategy switch time each year
            self.strategy_switch_time -= 1


def sigmoid(x):
    """The following part contains helping stuff"""
    return 0.5 * (np.tanh(x) + 1)