# -*- coding: utf-8 -*-
# Copyright Duncan Macleod 2017
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

from operator import itemgetter

from . import (api, datasets, utils)


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

    def _event_version_segment(event):
        versions = api._find_catalog_event_versions(event, host=host)
        last = versions[-1]
        dataset = "{0}_R{1}".format(event, last)
        metadata = api.fetch_event_json(event, host=host)
        return (
            dataset,
            utils.urllist_extent(map(itemgetter("url"), metadata["strain"])),
        )

    def _run_segment(run):
        return run, datasets.run_segment(run, host=host)

    # -- match datasets

    dataset_segments = [
        ("event", _event_version_segment),
        ("run", _run_segment),
    ]

    duration = end-start
    epochs = []

    for dstype, _dataset_segment in dataset_segments:
        dsets = datasets.find_datasets(
            type=dstype,
            detector=detector,
            segment=(start, end),
            host=host,
        )
        for dataset in dsets:
            dataset, segment = _dataset_segment(dataset)
            overlap = min(end, segment[1]) - max(start, segment[0])
            epochs.append((dataset, duration-overlap))

    if not epochs:
        raise ValueError(
            "No datasets found matching [{}, {})".format(start, end))

    return sorted(epochs, key=itemgetter(1, 0))[0][0]
