"""Run script for InSEEDS with LPJmL coupling"""

from pycoupler.config import read_config
from pycoupler.run import start_lpjml, check_lpjml

# Settings ================================================================== #

# paths
sim_path = "./simulations"
model_path = "./LPJmL"

spinup = True

# search for country code by supplying country name
# search_country("netherlands")
country_code = "NLD"

# Configuration ============================================================= #

# create config for spinup run
config_spinup = read_config(
    file_name="lpjml_config.cjson", model_path=model_path, spin_up=True
)

# set spinup run configuration
config_spinup.set_spinup(sim_path)

# only for global runs = TRUE
config_spinup.river_routing = False

# regrid by country - create new (extracted) input files and update config
config_spinup.regrid(sim_path, country_code=country_code, overwrite=False)

# write config (Config object) as json file
config_spinup_fn = config_spinup.to_json()

# create config for historic run
config_historic = read_config(
    file_name="lpjml_config.cjson", model_path=model_path
)

# set historic run configuration
config_historic.set_transient(
    sim_path,
    sim_name="historic_run",
    dependency="spinup",
    start_year=1901,
    end_year=2000,
)

# only for global runs = TRUE
config_historic.river_routing = False
config_historic.tillage_type = "read"
config_historic.residue_treatment = "read_residue_data"

config_historic.separate_harvests = False

# regrid by country - create new (extracted) input files and update config
config_historic.regrid(sim_path, country_code=country_code, overwrite=False)

# write config (Config object) as json file
config_historic_fn = config_historic.to_json()


# Simulations =============================================================== #

# check if everything is set correct
check_lpjml(config_file=config_spinup_fn)

# run spinup job
start_lpjml(config_file=config_spinup_fn)

# check if everything is set correct
check_lpjml(config_historic_fn)

# run spinup job
start_lpjml(config_file=config_historic_fn)
