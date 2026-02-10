# InSEEDS

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14265856.svg)](https://doi.org/10.5281/zenodo.14265856) [![CI](https://github.com/pik-copan/inseeds/actions/workflows/check.yml/badge.svg)](https://github.com/pik-copan/inseeds/actions) [![codecov](https://codecov.io/gh/pik-copan/inseeds/graph/badge.svg?token=JU73NURPI0)](https://codecov.io/gh/pik-copan/inseeds)


*Model of integrated social-ecological resilient land systems based on the [copan:LPJmL](https://github.com/pik-copan/pycopanlpjml) modeling framework*

## Overview

The InSEEDS model is designed to simulate the interactions between human
societies and ecosystems modeled by LPJmL in a spatially explicit manner.  
The model is codeveloped at the Potsdam Institute for Climate Impact Research
(PIK) and the Max Planck Institute of Geoanthropology in Jena.
InSEEDS builds on the [copan:LPJmL](https://github.com/pik-copan/pycopanlpjml) world-earth modeling framework that
inherits the entity and taxonomy system introduced for the
[copan:CORE framework](https://doi.org/10.5194/esd-11-395-2020).


### [Realisations](./inseeds/realisations)

InSEEDS provides multiple realisation classes which can be used to simulate different
aspects of the social-ecological system, depending how the model is build and
configured.  
**regenerative_tillage** is the first realisation implementation that simulates the
potential spreading of conservation tillage over conventional tillage in a
simplified farmer decision making model system.  

### [Components](./inseeds/components)

Each model is build on a set of components that represent the different
aspects of the social-ecological system. LPJmL is one component that is
defined in [pycopanlpjml](https://github.com/pik-copan/pycopanlpjml) and is used
to represent the ecological, earth system part of the model, the ENV and parts
of the MET taxon.  
Each component has various entities, e.g. the LPJmL world, the entire model
space and the cell, a single model unit, whereby the totality of all cells makes
up the world.  

[components/farming](./inseeds/components/farming) holds all farming components
that are used to simulate the direct agricultural part of the model.  
[components/farming/tillage_farmer](./inseeds/components/farming/tillage_farmer.py)
is a subcomponent of farming that focuses solely on the tillage management in
the agricultural system.  
Each subcomponent has various entities again, for example the farmer entity,
representing the decision making agent in the model.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install inseeds.

```bash
pip install .
```

Please clone and compile [LPJmL](https://github.com/pik/LPJmL) in advance.  
Make sure to also have set the [working environment for LPJmL](https://github.com/PIK-LPJmL/LPJmL/blob/master/INSTALL) correctly if you are not working
on the PIK HPC (with Slurm Workload Manager).  
The PIK python libraries [pycoupler](https://github.com/PIK-LPJmL/pycoupler),
[pycopancore](https://github.com/pik-copan/pycopancore),
as well as [pycopanlpjml](https://github.com/pik-copan/pycopanlpjml)
are required as they build framework that serves as the model base for InSEEDS.

See [scripts](./scripts/) for examples on how to use the model.

## Questions / Problems

In case of questions please contact the author team or [open an issue](https://github.com/pik-copan/inseeds/issues/new).

## Contributing
Merge requests are welcome, see [CONTRIBUTING.md](CONTRIBUTING.md). For major changes, please open an issue first to discuss what you would like to change.
