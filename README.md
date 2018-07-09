[![PyPI Release](https://badge.fury.io/py/gwosc.svg)](http://badge.fury.io/py/gwosc)
[![Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1196306.svg)](https://doi.org/10.5281/zenodo.1196306)
[![License](https://img.shields.io/pypi/l/gwosc.svg)](https://choosealicense.com/licenses/mit/)
![Python Versions](https://img.shields.io/pypi/pyversions/gwosc.svg)

[![TravisCI Build](https://travis-ci.com/gwpy/gwosc.svg?branch=develop)](https://travis-ci.com/gwpy/gwosc)
[![Appveyor Build](https://ci.appveyor.com/api/projects/status/t1xsjb4kieunjp66?svg=true)](https://ci.appveyor.com/project/gwpy/gwosc)
[![CircleCI Build](https://circleci.com/gh/gwpy/gwosc/tree/develop.svg?style=svg)](https://circleci.com/gh/gwpy/gwosc/tree/develop)
[![Coverage Status](https://coveralls.io/repos/github/gwpy/gwosc/badge.svg?branch=develop)](https://coveralls.io/github/gwpy/gwosc?branch=develop)
[![Maintainability](https://api.codeclimate.com/v1/badges/234aad1c71f0642d3e60/maintainability)](https://codeclimate.com/github/gwpy/gwosc/maintainability)

The `gwosc` package provides an interface to querying the open data
releases hosted on <https://losc.ligo.org> from the LIGO and Virgo
gravitational-wave observatories.

To install:

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
['https://losc.ligo.org//s/events/GW150914/H-H1_LOSC_4_V2-1126259446-32.hdf5', 'https://losc.ligo.org//s/events/GW150914/L-L1_LOSC_4_V2-1126259446-32.hdf5', 'https://losc.ligo.org//s/events/GW150914/H-H1_LOSC_4_V2-1126257414-4096.hdf5', 'https://losc.ligo.org//s/events/GW150914/L-L1_LOSC_4_V2-1126257414-4096.hdf5']
```

You can down-select the URLs using keyword arguments:

```python
>>> get_event_urls('GW150914', detector='L1', duration=32)
['https://losc.ligo.org//s/events/GW150914/L-L1_LOSC_4_V2-1126259446-32.hdf5']
```

## Locating data URLs by GPS interval

You can search for remote data URLs based on the GPS time interval as
follows:

```python
>>> from gwosc.locate import get_urls
>>> get_urls('L1', 968650000, 968660000)
['https://losc.ligo.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968646656-4096.hdf5', 'https://losc.ligo.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968650752-4096.hdf5', 'https://losc.ligo.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968654848-4096.hdf5', 'https://losc.ligo.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968658944-4096.hdf5']
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
science run, see [the O1 data release page](https://losc.ligo.org/O1/)
(*Data Quality*).

