"""Submit script for InSEEDS with LPJmL coupling"""

from pycoupler.config import read_config
from pycoupler.run import check_lpjml, submit_lpjml
import sys


# Settings ================================================================== #

import pathlib
runscript_folder = pathlib.Path(__file__).parent.resolve()

# paths
sim_path = f"{runscript_folder}/simulations"
model_path = f"{runscript_folder}/LPJmL"
inseeds_config_file = (
    f"{runscript_folder}/inseeds/models/regenerative_tillage/config.yaml"  # noqa"
)

# Configuration ============================================================= #

# create config for coupled run
config_coupled = read_config(
    model_path=model_path, file_name="lpjml_config.cjson"
)

# set coupled run configuration
config_coupled.set_coupled(
    sim_path,
    sim_name="coupled_global",
    dependency="historic_run",
    start_year=2001,
    end_year=2050,
    coupled_year=2023,
    coupled_input=["with_tillage"],
    coupled_output=[
        "soilc_agr_layer",
        "cftfrac",
        "harvestc",
        "hdate",
        "country",
        "terr_area",
    ],
)

# only for single cells runs
config_coupled.outputyear = 2022

# set more recent input files
config_coupled.fix_co2 = True
config_coupled.fix_co2_year = 2022
config_coupled.fix_climate = True
config_coupled.fix_climate_cycle = 11
config_coupled.fix_climate_year = 2013

config_coupled.tillage_type = "read"
config_coupled.residue_treatment = "read_residue_data"

config_coupled.add_config(inseeds_config_file)

# write config (Config object) as json file
config_coupled_fn = config_coupled.to_json()


# Simulations =============================================================== #

# check if everything is set correct
check_lpjml(config_coupled_fn)

# run lpjml simulation for coupling in the background
submit_lpjml(
    config_file=config_coupled_fn,
    couple_to=f"{runscript_folder}/inseeds/inseeds/models/regenerative_tillage/main.py",
    venv_path=sys.prefix,
    wtime="5:00:00",
)
