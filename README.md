# The LIGO Open Science Center Python API

The ``losc`` package provides an interface to querying and discovering data files hosted on https://losc.ligo.org as part of the open data releases from the LIGO Scientific Collaboration.

To install:

```
pip install losc
```

Then you can search for remote data URLs as follows:

```python
>>> from losc.locate import get_urls
>>> get_urls('L1', 968654552, 968654562)
['https://losc.ligo.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968650752-4096.hdf5']
```

This arguments for this function are as follows

- `detector` : the prefix of the relevant gravitational-wave interferometer, either `'H1'` for LIGO-Hanford, or `'L1'` for LIGO Livingston,
- `start`: the GPS start time of the interval of interest
- `end`: the GPS end time of the interval of interest

By default, this method will return the paths to HDF5 files for the 4 kHz sample-rate data, these can be specified as keyword arguments. For full information, run

```python
>>> help(get_urls)
```
