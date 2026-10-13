"""Run script for InSEEDS with LPJmL coupling"""

from pycoupler.config import read_config
from pycoupler.run import operate_lpjml, check_lpjml
from pathlib import Path

from inseeds.models.regenerative_tillage import Model  # noqa

# Settings ================================================================== #

runscript_folder = Path(__file__).parent.resolve()

# At this path, all outputs, generated input files, runscripts and configs
# will be saved.
sim_path = f"{runscript_folder}/simulations"

# This is the path to the config file for the InSEEDS model
# from this repository.
inseeds_config_file = (
    f"{runscript_folder}/inseeds/models/regenerative_tillage/config.yaml"
)

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

config_coupled = read_config(
    model_path=model_path,
    file_name=base_config_file,
    parse_in_container=parse_in_container,
)
config_coupled.inpath = inpath

# LPJmL config -------------------------------------------------------------- #

# Some inputs are not relevant depending on the simulation.
# To ignore them, remove them from the base config:
del config_coupled.input.ignition
del config_coupled.input.maxfiresize
del config_coupled.input.burntarea

# Here you can set the base settings for the run
config_coupled.set_coupled(
    sim_path,
    sim_name="coupled_test",
    dependency="historic_run",
    start_year=2001,
    end_year=2100,
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

# You can edit the config settings to change the configuration for LPJmL.
# Some of the config parameters are documented in lpjml_config.cjson. Be careful
# to choose parameters that are compatible with the runs you depend on.
# Here are examples of a typical configuration:

# The outputyear usually is the simulation start year, but you can also choose to
# output data only later, e.g. a year before coupling starts:
config_coupled.outputyear = 2022

# Fix the CO2 and climate for years were no data is
# available (if you don’t want to supply climate scenarios etc.)
config_coupled.fix_co2 = True
config_coupled.fix_co2_year = 2022
config_coupled.fix_climate = True
config_coupled.fix_climate_cycle = 11
config_coupled.fix_climate_year = 2013

# This is how you would load a climate scenario instead
# (Refer to https://gitlab.pik-potsdam.de/lpjml/LPJmL_internal/-/wikis/Input#climate
# for other climate inputs):
# scenario_path = Path("/path/to/climate/scenario")
# for var in ["prec", "temp", "tmax", "tmin", "lwnet", "swdown", "humid", "wind", "co2"]:
#     getattr(config_coupled, var).name = scenario_path / f"{var}_2015-2100.clm"
#     getattr(config_coupled, var).fmt = "clm"

# For a small run with only one country, river routing won’t work
# so disable it:
config_coupled.river_routing = False

# This has to be 'read' for InSEEDS to work
config_coupled.tillage_type = "read"
# This has to be 'read_residue_data' for InSEEDS to work
config_coupled.residue_treatment = "read_residue_data"


# This method extracts the smaller grid for the selected country from
# the input data and writes it to your input folder. It is essential,
# if you want to run on a smaller grid.
config_coupled.regrid(sim_path, country_code=country_code, overwrite=False)

# InSEEDS config ------------------------------------------------------------ #

# Add the default config for the coupled model to document all parameters.
config_coupled.add_config(inseeds_config_file)

# Now you can modify the config for the coupled model, such as setting the
# pioneer_share:
config_coupled.coupled_config.pioneer_share = 0.25

# Save the config to JSON for reproducibility
config_coupled_file = config_coupled.to_json()


# Simulations =============================================================== #

# Check if everything is set correctly for LPJmL
# (otherwise this will fail, producing an error output).
check_lpjml(config_coupled_file)

# run lpjml simulation for coupling in the background
lpjml_process = operate_lpjml(
    config_file=config_coupled_file,
    std_to_file=False,  # this gives you an output in your current terminal
    wait_for_exit=False,  # LPJmL needs to run in a separate process
)

# InSEEDS run --------------------------------------------------------------- #

try:
    # This is baiscally the same as your `main.py`.
    # It initializes the model you imported at the top of the file:
    model = Model(
        config_file=config_coupled_file,
        lpjml_host="0.0.0.0",
        lpjml_port=2224,
    )

    # And then it waits for LPJmL to exchange the data each year:
    for year in model.lpjml.get_sim_years():
        model.update(year)
finally:
    # There was an error or the Model finished, stop LPJmL gracefully
    lpjml_process.terminate()
