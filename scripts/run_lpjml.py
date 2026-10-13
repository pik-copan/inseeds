"""Run script for InSEEDS with LPJmL coupling"""

from pycoupler.config import read_config
from pycoupler.run import operate_lpjml, check_lpjml
from pathlib import Path

# Settings ================================================================== #

runscript_folder = Path(__file__).parent.resolve()

# At this path, all outputs, generated input files, runscripts and configs
# will be saved.
sim_path = f"{runscript_folder}/simulations"

# If you want to use a compiled LPJmL version in a particular folder,
# uncomment this line and add the path to your LPJmL folder:
# model_path = f"{runscript_folder}/LPJmL"
# parse_in_container = False

# Alternatively, you can run LPJmL from a container. To do so,
# leave model_path as None and set parse_in_container to the path
# to the container image. You can also just set it to True; in this case,
# the path set in you environment variable LPJML_CONTAINER will be used.
# This might e.g. be the case if you load the LPJmL container as a module.
model_path = None
parse_in_container = True

# Here, set the path where your input files are located. All input files in
# the config with relative paths will use this path as a base.
inpath = ""

# This is the path to the default config to load as a base for your run.
# It can be relative to the model_path or a path in the container.
base_config_file = "lpjml_config.cjson"
# In the container this typically is:
# base_config_file = "/opt/lpjml/lpjml_config.cjson"

# If you want to run your simulation on a smaller than global grid, you can
# regrid to just a single country. You need to set the ISO3 country code here,
# which you can get using search_country("Netherlands").
country_code = "NLD"

# Configuration ============================================================= #

# Spinup run ---------------------------------------------------------------- #
# This run intializes the natural vegetation and gives the virtual soils time to
# reach equilibrium.

spinup_name = "spinup"

config_spinup = read_config(
    model_path=model_path,
    file_name=base_config_file,
    parse_in_container=parse_in_container,
    spinup=True,
)
config_spinup.inpath = inpath

# Some inputs are not relevant depending on the simulation.
# To ignore them, remove them from the base config:
del config_spinup.input.ignition
del config_spinup.input.maxfiresize
del config_spinup.input.burntarea

config_spinup.set_spinup(sim_path, spinup_name)

# Change the default spinup configuration, e.g. for a shorter run.
# You can read more at https://gitlab.pik-potsdam.de/lpjml/LPJmL_internal/-/wikis/Configuration
# These are the current defaults:
# config_spinup.firstyear = 1700
# config_spinup.lastyear = 1700
# config_spinup.nspinup = 3799
# config_spinup.outputyear = -2099
# config_spinup.restart_year = 1700
# config_spinup.equilsoil = True
config_spinup.river_routing = False  # This should be false for small grids

# This method extracts the smaller grid for the selected country from
# the input data and writes it to your input folder. It is essential,
# if you want to run on a smaller grid.
config_spinup.regrid(sim_path, country_code=country_code, overwrite=False)

# Save the config to JSON for reproducibility
config_spinup_fn = config_spinup.to_json()

# Historic run -------------------------------------------------------------- #
# This run simulates the historic agricultural patterns from the given data up until
# the point where the coupled run should pick up.

config_historic = read_config(
    model_path=model_path,
    file_name=base_config_file,
    parse_in_container=parse_in_container,
)
config_historic.inpath = inpath

# set historic run configuration
config_historic.set_transient(
    sim_path,
    sim_name="historic_run",
    dependency=spinup_name,
    start_year=1901,  # This is the default, LPJmL adds additional spinup years in between
    end_year=2000,
)

# Some inputs are not relevant depending on the simulation.
# To ignore them, remove them from the base config:
del config_historic.input.ignition
del config_historic.input.maxfiresize
del config_historic.input.burntarea

# Change the default configuration for the historic run, e.g. for a shorter run.
# You can read more at https://gitlab.pik-potsdam.de/lpjml/LPJmL_internal/-/wikis/Configuration
# These settings are required for InSEEDS to start with tillage practices set up
# with historic data.
config_historic.tillage_type = "read"
config_historic.residue_treatment = "read_residue_data"
config_historic.river_routing = False  # This should be false for small grids

# This method extracts the smaller grid for the selected country from
# the input data and writes it to your input folder. It is essential,
# if you want to run on a smaller grid.
config_historic.regrid(sim_path, country_code=country_code, overwrite=False)

# Save the config to JSON for reproducibility
config_historic_fn = config_historic.to_json()


# Simulations =============================================================== #

# Check if everything is set correctly for the spinup run
# (otherwise this will fail, producing an error output).
check_lpjml(config_file=config_spinup_fn)

# Run the spinup job serially and wait until it is done.
operate_lpjml(
    config_file=config_spinup_fn,
    std_to_file=False,  # this gives you an output in your current terminal
)

# Check if everything is set correctly for the historic run
# (otherwise this will fail, producing an error output).
check_lpjml(config_historic_fn)

# Run the hisrtoric job serially and wait until it is done.
operate_lpjml(
    config_file=config_historic_fn,
    std_to_file=False,  # this gives you an output in your current terminal
)
