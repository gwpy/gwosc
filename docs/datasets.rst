Querying dataset information
=============================

To search for available datasets (correct as of March 14 2018):

.. code:: python

    >>> from gwosc import datasets
    >>> datasets.find_datasets()
    ['GW150914', 'GW151226', 'GW170104', 'GW170608', 'GW170814', 'GW170817', 'LVT151012', 'O1', 'S5', 'S6']
    >>> datasets.find_datasets(detector='V1')
    ['GW170814', 'GW170817']
    >>> datasets.find_datasets(type='run')
    ['O1', 'S5', 'S6']

To query for the GPS time of an event dataset (or vice-versa):

.. code:: python

    >>> datasets.event_gps('GW170817')
    1187008882.43
    >>> datasets.event_at_gps(1187008882)
    'GW170817'

Similar queries are available for observing run datasets:

.. code:: python

    >>> datasets.run_segment('O1')
    (1126051217, 1137254417)
    >>> datasets.run_at_gps(1135136350)  # event_gps('GW151226')
    'O1'

`gwosc.datasets` reference
--------------------------

.. automodule:: gwosc.datasets
    :members:
    :undoc-members:
    :show-inheritance:
