"""Run script for InSEEDS with LPJmL coupling"""

import pickle

from pycoupler.config import read_config
from pycoupler.run import start_lpjml, check_lpjml

from inseeds.realisations.regenerative_tillage import Model  # noqa

# Settings ================================================================== #

# paths
sim_path = "./simulations"
model_path = "./LPJmL"
inseeds_config_file = (
    "./inseeds/realisations/regenerative_tillage/config.yaml"  # noqa"
)

# search for country code by supplying country name
# search_country("netherlands")
country_code = "NLD"

# Configuration ============================================================= #

# create config for coupled run
config_coupled = read_config(
    model_path=model_path, file_name="lpjml_config.cjson"
)

# set coupled run configuration
config_coupled.set_coupled(
    sim_path,
    sim_name="coupled_test",
    dependency="historic_run",
    start_year=2001,
    end_year=2030,
    coupled_year=2023,
    coupled_input=["with_tillage"],  # residue_on_field
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

config_coupled.fix_co2 = True
config_coupled.fix_co2_year = 2022
config_coupled.fix_climate = True
config_coupled.fix_climate_cycle = 11
config_coupled.fix_climate_year = 2013

# only for global runs = TRUE
config_coupled.river_routing = False

config_coupled.tillage_type = "read"
config_coupled.residue_treatment = "read_residue_data"
config_coupled.double_harvest = False

# regrid by country - create new (extracted) input files and update config file
config_coupled.regrid(
    sim_path, country_code=country_code, overwrite_input=False
)

config_coupled.add_config(inseeds_config_file)

# set InSEEDS configuration: here we set the pioneer share to 0.25
config_coupled.coupled_config.pioneer_share = 0.25

# write config (Config object) as json file
config_coupled_fn = config_coupled.to_json()


# Simulations =============================================================== #

# check if everything is set correct
check_lpjml(config_coupled_fn)

# run lpjml simulation for coupling in the background
start_lpjml(
    config_file=config_coupled_fn,
    std_to_file=False,  # write stdout and stderr to file
)

# InSEEDS run --------------------------------------------------------------- #

model = Model(config_file=config_coupled_fn)

# write config as json
model.lpjml.config.to_json("./inseeds/tests/data/config.json")

# write input and output data to pickle files
with open("./inseeds/tests/data/lpjml_input.pkl", "wb") as outp:
    pickle.dump(model.world.to_earth, outp, pickle.HIGHEST_PROTOCOL)

with open("./inseeds/tests/data/lpjml_output.pkl", "wb") as outp:
    pickle.dump(model.world.from_earth, outp, pickle.HIGHEST_PROTOCOL)

with open("./inseeds/tests/data/lpjml.pkl", "wb") as lpj:
    pickle.dump(model.lpjml, lpj, pickle.HIGHEST_PROTOCOL)
