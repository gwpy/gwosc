# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University, 2018-2020
#
# This file is part of GWOSC.
#
# GWOSC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GWOSC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GWOSC.  If not, see <http://www.gnu.org/licenses/>.

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
        the URL of the remote LOSC server

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
        host, dataset, flag, start, end-start)


def _find_dataset(start, end, detector, host=api.DEFAULT_URL):

    # -- utility methods to resolve a (proper) dataset name and its segment

    def _event_segment(event):
        raw = api._fetch_allevents_event_json(event, host=host)["events"]
        dataset, meta = list(raw.items())[0]
        return (
            dataset,
            datasets.event_segment(
                dataset,
                catalog=meta["catalog.shortName"],
                version=meta["version"],
                host=host,
            ),
        )

    def _run_segment(run):
        return run, datasets.run_segment(run, host=host)

    # -- match datasets

    dataset_segments = [
        ("event", _event_segment),
        ("run", _run_segment),
    ]

    duration = end-start
    epochs = []

    for dstype, _dataset_segment in dataset_segments:
        for dataset in datasets._iter_datasets(
                type=dstype,
                detector=detector,
                segment=(start, end),
                host=host,
        ):
            try:
                dataset, segment = _dataset_segment(dataset)
            except ValueError as exc:
                if str(exc) == (
                    "no event datasets found for {!r}".format(dataset)
                ):
                    continue
                raise
            overlap = min(end, segment[1]) - max(start, segment[0])
            epochs.append((dataset, duration-overlap))

    if not epochs:
        raise ValueError(
            "No datasets found matching [{}, {})".format(start, end))

    return sorted(epochs, key=itemgetter(1, 0))[0][0]
