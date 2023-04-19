# `gwosc` client API

The `gwosc` package provides an interface to querying the open data
releases hosted on <https://gwosc.org> from the GEO, LIGO,
and Virgo gravitational-wave observatories.

## Release status

[![PyPI version](https://badge.fury.io/py/gwosc.svg)](http://badge.fury.io/py/gwosc)
[![Conda version](https://img.shields.io/conda/vn/conda-forge/gwosc.svg)](https://anaconda.org/conda-forge/gwosc/)  
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1196306.svg)](https://doi.org/10.5281/zenodo.1196306)
[![License](https://img.shields.io/pypi/l/gwosc.svg)](https://choosealicense.com/licenses/mit/)
![Supported Python versions](https://img.shields.io/pypi/pyversions/gwosc.svg)

## Development status

[![Build status](https://git.ligo.org/gwosc/client/badges/main/pipeline.svg)](https://git.ligo.org/gwosc/client/-/pipelines)
![Code coverage](https://git.ligo.org/gwosc/client/badges/main/coverage.svg)
[![Documentation](https://readthedocs.org/projects/gwosc/badge/?version=latest)](https://gwosc.readthedocs.io/en/latest/?badge=latest)

## Installation

To install:

    conda install -c conda-forge gwosc

or

    pip install gwosc

## Searching for datasets

To search for available datasets (correct as of March 14 2018):

```python
>>> from gwosc import datasets
>>> datasets.find_datasets()
['GW150914', 'GW151226', 'GW170104', 'GW170608', 'GW170814', 'GW170817', 'LVT151012', 'O1', 'S5', 'S6']
>>> datasets.find_datasets(detector='V1')
['GW170814', 'GW170817']
>>> datasets.find_datasets(type='run')
['O1', 'S5', 'S6']
```

To query for the GPS time of an event dataset (or vice-versa):

```python
>>> datasets.event_gps('GW170817')
1187008882.43
>>> datasets.event_at_gps(1187008882)
'GW170817'
```

Similar queries are available for observing run datasets:

```python
>>> datasets.run_segment('O1')
(1126051217, 1137254417)
>>> datasets.run_at_gps(1135136350)  # event_gps('GW151226')
'O1'
```

## Locating data URLs by event name

You can search for remote data URLS based on the event name:

```python
>>> from gwosc.locate import get_event_urls
>>> get_event_urls('GW150914')
['https://gwosc.org/eventapi/json/GWTC-1-confident/GW150914/v3/H-H1_GWOSC_4KHZ_R1-1126259447-32.hdf5', 'https://gwosc.org/eventapi/json/GWTC-1-confident/GW150914/v3/H-H1_GWOSC_4KHZ_R1-1126257415-4096.hdf5', 'https://gwosc.org/eventapi/json/GWTC-1-confident/GW150914/v3/L-L1_GWOSC_4KHZ_R1-1126259447-32.hdf5', 'https://gwosc.org/eventapi/json/GWTC-1-confident/GW150914/v3/L-L1_GWOSC_4KHZ_R1-1126257415-4096.hdf5']
```

You can down-select the URLs using keyword arguments:

```python
>>> get_event_urls('GW150914', detector='L1', duration=32)
['https://gwosc.org/eventapi/json/GWTC-1-confident/GW150914/v3/L-L1_GWOSC_4KHZ_R1-1126259447-32.hdf5']
```

## Locating data URLs by GPS interval

You can search for remote data URLs based on the GPS time interval as
follows:

```python
>>> from gwosc.locate import get_urls
>>> get_urls('L1', 968650000, 968660000)
['https://gwosc.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968646656-4096.hdf5', 'https://gwosc.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968650752-4096.hdf5', 'https://gwosc.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968654848-4096.hdf5', 'https://gwosc.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968658944-4096.hdf5']
```

This arguments for this function are as follows

-   `detector` : the prefix of the relevant gravitational-wave
    interferometer, either `'H1'` for LIGO-Hanford, or `'L1'` for LIGO
    Livingston,
-   `start`: the GPS start time of the interval of interest
-   `end`: the GPS end time of the interval of interest

By default, this method will return the paths to HDF5 files for the 4
kHz sample-rate data, these can be specified as keyword arguments. For
full information, run

```python
>>> help(get_urls)
```

## Query for Timeline segments

You can also search for Timeline segments, based on a flag name, and a
GPS time interval as follows:

```python
>>> from gwosc.timeline import get_segments
>>> get_segments('H1_DATA', 1126051217, 1126151217)
[(1126073529, 1126114861), (1126121462, 1126123267), (1126123553, 1126126832), (1126139205, 1126139266), (1126149058, 1126151217)]
```

The output is a `list` of `(start, end)` 2-tuples which each represent a
semi-open time interval.

For documentation on what flags are available, for example for the O1
science run, see [the O1 data release page](https://gwosc.org/O1/)
(*Data Quality*).

