Querying for data file URLs
============================

Locating data URLs by event name
---------------------------------

You can search for remote data URLS based on the event name:

.. code:: python

    >>> from gwopensci.locate import get_event_urls
    >>> get_event_urls('GW150914')
    ['https://losc.ligo.org//s/events/GW150914/H-H1_LOSC_4_V2-1126259446-32.hdf5', 'https://losc.ligo.org//s/events/GW150914/L-L1_LOSC_4_V2-1126259446-32.hdf5', 'https://losc.ligo.org//s/events/GW150914/H-H1_LOSC_4_V2-1126257414-4096.hdf5', 'https://losc.ligo.org//s/events/GW150914/L-L1_LOSC_4_V2-1126257414-4096.hdf5']

You can down-select the URLs using keyword arguments:

.. code:: python

    >>> get_event_urls('GW150914', detector='L1', duration=32)
    ['https://losc.ligo.org//s/events/GW150914/L-L1_LOSC_4_V2-1126259446-32.hdf5']


Locating data URLs by GPS interval
----------------------------------

You can search for remote data URLs based on the GPS time interval as
follows:

.. code:: python

    >>> from gwopensci.locate import get_urls
    >>> get_urls('L1', 968650000, 968660000)
    ['https://losc.ligo.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968646656-4096.hdf5', 'https://losc.ligo.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968650752-4096.hdf5', 'https://losc.ligo.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968654848-4096.hdf5', 'https://losc.ligo.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968658944-4096.hdf5']

This arguments for this function are as follows

-  ``detector`` : the prefix of the relevant gravitational-wave
   interferometer, either ``'H1'`` for LIGO-Hanford, or ``'L1'`` for
   LIGO Livingston,
-  ``start``: the GPS start time of the interval of interest
-  ``end``: the GPS end time of the interval of interest

By default, this method will return the paths to HDF5 files for the 4
kHz sample-rate data, these can be specified as keyword arguments. For
full information, run

.. code:: python

    >>> help(get_urls)

gwopensci.locate reference
--------------------------

.. automodule:: gwopensci.locate
    :members:
    :undoc-members:
    :show-inheritance:
