import os
import argparse

from pycoupler.coupler import LPJmLCoupler
from inseeds.models.capital_farming import Model


def run_inseeds(config_file):
    """Run the INSEEDS model with the given configuration file"""
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"{config_file} does not exist")

    model = Model(config_file=config_file)

    for year in model.lpjml.get_sim_years():
        model.update(year)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="Path to the configuration file")
    args = parser.parse_args()

    run_inseeds(args.config_file)

# execute program via
# python inseeds.py /path/to/config_coupled_fn.json
