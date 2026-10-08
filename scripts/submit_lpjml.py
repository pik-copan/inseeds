"""Submit script for spinup and historic LPJmL simulations.

This sets up the dependency runs, spinning up the natural vegetation for
the coupled runs. You might not need to run these as often, so they are
split in a different file.
"""

from pycoupler.config import read_config
from pycoupler.run import check_lpjml, submit_lpjml
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


# Configuration ============================================================= #

# Spinup run ---------------------------------------------------------------- #
# This run intializes the natural vegetation and gives the virtual soils time to
# reach equilibrium.

spinup_name = "spinup"

config_spinup = read_config(
    model_path=model_path,
    file_name=base_config_file,
    parse_in_container=parse_in_container,
    spinup=True,  # This is important for the spinup run
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
# config_spinup.river_routing = False

# Save the config to JSON for reproducibility.
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

# Save the config to JSON for reproducibility.
config_historic_fn = config_historic.to_json()


# Simulations =============================================================== #

# Check if everything is set correctly for LPJmL
# (otherwise this will fail, producing an error output).
check_lpjml(config_spinup_fn)

# Send the simulation off as a SLURM job,
# Edit this to fit your particular HPC setup.
# In particular, edit the partition, sclass, and modules settings

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

spinup_job_id = submit_lpjml(
    config_file=config_spinup_fn,
    # Give a time estimation of when the job will terminate.
    # This allows the scheduler to prioritize it more easily.
    wtime="1:00:00",
    ntasks=512,
    sclass=sclass,
    partition=partition,
    modules=modules,
    account=account,
)

check_lpjml(config_historic_fn)

# exactly as above
submit_lpjml(
    config_file=config_historic_fn,
    wtime="0:30:00",
    ntasks=512,
    # This job depends on the previous spinup job and waits in the queue for
    # its completion:
    dependency=spinup_job_id,
    sclass=sclass,
    partition=partition,
    modules=modules,
    account=account,
)
