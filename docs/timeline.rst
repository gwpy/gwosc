Querying for Timeline segments
==============================

You can search for Timeline segments, based on a flag name, and a
GPS time interval as follows:

.. code:: python

    >>> from gwosc.timeline import get_segments
    >>> get_segments('H1_DATA', 1126051217, 1126151217)
    [(1126073529, 1126114861), (1126121462, 1126123267), (1126123553, 1126126832), (1126139205, 1126139266), (1126149058, 1126151217)]

The output is a ``list`` of ``(start, end)`` 2-tuples which each
represent a semi-open time interval.

For documentation on what flags are available, for example for the O1
science run, see `the O1 data release
page <https://losc.ligo.org/O1/>`__ (*Data Quality*).

gwosc.timeline reference
------------------------

.. automodule:: gwosc.timeline
    :members:
    :undoc-members:
    :show-inheritance:
