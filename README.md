# FaaS benchmarking analysis

This repository contains methods and visualization methods for analyzing
benchmarking raw data generated by faastermetrics experiments.


## Setup

This project is best run inside of a [conda](https://docs.conda.io/en/latest/).

Install miniconda for your system following the [official
instructions](https://docs.conda.io/en/latest/miniconda.html).

After installation you should have:

* `conda` as an executable in your $PATH

Now setup a new conda environment based on the `environment.yml` given in this
project.

```sh
$ conda env create -f environment.yml
```

Make sure to activate the correct conda environment before running anything.

```
$ conda activate faastermetrics
$ conda env list  # check that the env is properly installed and activated
> # conda environments:
> #
> base                     /Users/max/miniconda
> faastermetrics        *  /Users/max/miniconda/envs/faastermetrics
```

### Development install

Install the faastermetrics from the current repository by executing setup.py in
development mode:

```
$ python setup.py develop
```

A development version can also be uninstalled by using: `python setup.py develop
--uninstall`.
