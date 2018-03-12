# The LIGO Open Science Center Python API

[![Build Status](https://travis-ci.org/duncanmmacleod/python-losc.svg?branch=develop)](https://travis-ci.org/duncanmmacleod/python-losc)
[![Coverage Status](https://coveralls.io/repos/github/duncanmmacleod/python-losc/badge.svg?branch=develop)](https://coveralls.io/github/duncanmmacleod/python-losc?branch=develop)

The ``losc`` package provides an interface to querying and discovering data files hosted on https://losc.ligo.org as part of the open data releases from the LIGO Scientific Collaboration.

To install:

```
pip install losc
```

## Query by event name

You can search for remote data URLS based on the event name:

```python
>>> from losc.locate import get_event_urls
>>> get_event_urls('GW150914')
['https://losc.ligo.org//s/events/GW150914/H-H1_LOSC_4_V2-1126259446-32.hdf5', 'https://losc.ligo.org//s/events/GW150914/L-L1_LOSC_4_V2-1126259446-32.hdf5', 'https://losc.ligo.org//s/events/GW150914/H-H1_LOSC_4_V2-1126257414-4096.hdf5', 'https://losc.ligo.org//s/events/GW150914/L-L1_LOSC_4_V2-1126257414-4096.hdf5']
```

You can down-select the URLs using keyword arguments:

```python
>>> get_event_urls('GW150914', detector='L1', duration=32)
['https://losc.ligo.org//s/events/GW150914/L-L1_LOSC_4_V2-1126259446-32.hdf5']
```


## Query by GPS interval

You can search for remote data URLs based on the GPS time interval as follows:

```python
>>> from losc.locate import get_urls
>>> get_urls('L1', 968650000, 968660000)
['https://losc.ligo.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968646656-4096.hdf5',
 'https://losc.ligo.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968650752-4096.hdf5',
 'https://losc.ligo.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968654848-4096.hdf5',
 'https://losc.ligo.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968658944-4096.hdf5']
```

This arguments for this function are as follows

- `detector` : the prefix of the relevant gravitational-wave interferometer, either `'H1'` for LIGO-Hanford, or `'L1'` for LIGO Livingston,
- `start`: the GPS start time of the interval of interest
- `end`: the GPS end time of the interval of interest

By default, this method will return the paths to HDF5 files for the 4 kHz sample-rate data, these can be specified as keyword arguments. For full information, run

```python
>>> help(get_urls)
```


## Query for Timeline segments

You can also search for Timeline segments, based on a flag name, and a GPS time interval as follows::


```python
>>> from losc.timeline import get_segments
>>> get_segments('H1_DATA', 1126051217, 1126151217)
[(1126073529, 1126114861), (1126121462, 1126123267), (1126123553, 1126126832), (1126139205, 1126139266), (1126149058, 1126151217)]
```

The output is a `list` of `(start, end)` 2-tuples which each represent a semi-open time interval.

For documentation on what flags are available, for example for the O1 science run, see [the O1 data release page](https://losc.ligo.org/O1/) (_Data Quality_).
