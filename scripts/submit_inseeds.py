"""Submit script for InSEEDS with LPJmL coupling"""

from pycoupler.config import read_config
from pycoupler.run import check_lpjml, submit_lpjml
import importlib.resources
from pathlib import Path

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

# Configuration ============================================================= #

config_coupled = read_config(
    model_path=model_path,
    file_name=base_config_file,
    parse_in_container=parse_in_container,
)
config_coupled.inpath = inpath

# Some inputs are not relevant depending on the simulation.
# To ignore them, remove them from the base config:
del config_coupled.input.ignition
del config_coupled.input.maxfiresize
del config_coupled.input.burntarea

# Here you can set the base settings for the run
config_coupled.set_coupled(
    sim_path,
    sim_name="",  # You can choose any name here
    # This should be the name of the run on which data this one depends
    # Usually a spinup run.
    dependency="historic_run",
    start_year=2001,
    end_year=2050,
    coupled_year=2023,
    coupled_input=[
        # These inputs are sent to LPJmL from the model
        "with_tillage"
    ],
    coupled_output=[
        # These variables should be available to the model from LPJmL
        # while the simulation is running.
        # This is different from the variables written to output files.
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

# This has to be 'read' for InSEEDS to work
config_coupled.tillage_type = "read"
# This has to be 'read_residue_data' for InSEEDS to work
config_coupled.residue_treatment = "read_residue_data"


# Add the config for the coupled model to document all parameters.
config_coupled.add_config(inseeds_config_file)

# Save the config to JSON for reproducibility
config_coupled_file = config_coupled.to_json()


# Simulations =============================================================== #

# Check if everything is set correctly for LPJmL
# (otherwise this will fail, producing an error output).
check_lpjml(config_coupled_file)

# You can find out more about the available sclasses (or rather, qos specs)
# using: sacctmgr show qos format=name,priority
sclass = None  # e.g. short
# You can list the partitions using: sinfo
partition = None  # e.g. p.geany
# You can list the modules currently activated using: module list
modules = None  # e.g. "lpjml/6.1.7-gcc-openmpi"
# This is the account your usage will be attributed to.
# Which account you can use depends on your permissions on your cluster.
# List them using: sacctmgr show associations User=$USER format=Account,User
account = None  # e.g. "lpjml"

submit_lpjml(
    config_file=config_coupled_file,
    couple_to=importlib.resources.files("inseeds")
    / "models/regenerative_tillage/main.py",
    # Give a time estimation of when the job will terminate.
    # This allows the scheduler to prioritize it more easily.
    wtime="5:00:00",
    ntasks=512,
    dependency=spinup_job_id,
    sclass=sclass,
    partition=partition,
    modules=modules,
    account=account,
)
