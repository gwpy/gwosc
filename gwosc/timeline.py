# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2018-2021)
# SPDX-License-Identifier: MIT

"""
`gwosc.timeline` provides functions to find segments for a given dataset.

You can search for Timeline segments, based on a flag name, and a
GPS time interval as follows:

>>> from gwosc.timeline import get_segments
>>> get_segments('H1_DATA', 1126051217, 1126151217)
[(1126073529, 1126114861), (1126121462, 1126123267), (1126123553, 1126126832), (1126139205, 1126139266), (1126149058, 1126151217)]

The output is a `list` of ``[start, end)`` 2-tuples which each
represent a semi-open time interval.

For documentation on what flags are available, for example for the O1
science run, see `the O1 data release
page <https://gw-openscience.org/O1/>`__ (*Data Quality*).
"""  # noqa: E501

from operator import itemgetter

from . import (api, datasets)


def get_segments(flag, start, end, host=api.DEFAULT_URL):
    """Return the [start, end) GPS segments for this flag

    Parameters
    ----------
    flag : `str`
        name of flag, e.g. ``'H1_DATA'``

    start : `int`
        the GPS start time of your query

    end : `int`
        the GPS end time of your query

    host : `str`, optional
        the URL of the remote GWOSC server

    Returns
    -------
    segments : `list` of `(int, int)` tuples
        a list of `[a, b)` GPS segments
    """
    return list(map(tuple, api.fetch_json(
        timeline_url(flag, start, end, host=host))['segments']))


def timeline_url(flag, start, end, host=api.DEFAULT_URL):
    """Returns the Timeline JSON URL for a flag name and GPS interval
    """
    detector = flag.split('_', 1)[0]
    dataset = _find_dataset(start, end, detector, host=host)
    return '{}/timeline/segments/json/{}/{}/{}/{}/'.format(
        host, dataset, flag, start, end - start)


def _find_dataset(start, end, detector, host=api.DEFAULT_URL):
    duration = end - start
    epochs = []

    for run in datasets._iter_datasets(
            type="run",
            detector=detector,
            segment=(start, end),
            host=host,
    ):
        segment = datasets.run_segment(run, host=host)
        overlap = min(end, segment[1]) - max(start, segment[0])
        epochs.append((run, duration - overlap))

    if not epochs:
        raise ValueError(
            "No datasets found matching [{}, {})".format(start, end))

    return sorted(epochs, key=itemgetter(1, 0))[0][0]
