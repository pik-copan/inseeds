# InSEEDS

[![CI](https://github.com/pik-copan/inseeds/actions/workflows/check.yml/badge.svg)](https://github.com/pik-copan/inseeds/actions)

Model of integrated social-ecological resilient land systems based on the copan:CORE modeling framework using LPJmL

## Overview

...

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install inseeds.

```bash
pip install .
```

Please clone and compile [LPJmL](https://github.com/pik/LPJmL) in advance.  
Make sure to also have set the [working environment for LPJmL](https://github.com/PIK-LPJmL/LPJmL/blob/master/INSTALL) correctly if you are not working
on the PIK HPC (with Slurm Workload Manager).
The PIK python libraries [pycoupler](https://github.com/PIK-LPJmL/pycoupler) and [pycopancore](https://github.com/pik-copan/pycopancore) are required as they serve as the basis for InSEEDS.

See [scripts](./scripts/) for examples on how to use the package.

## Questions / Problems

In case of questions please contact Jannes Breier jannesbr@pik-potsdam.de or [open an issue](https://github.com/pik-copan/inseeds/issues/new).

## Contributing
Merge requests are welcome, see [CONTRIBUTING.md](CONTRIBUTING.md). For major changes, please open an issue first to discuss what you would like to change.