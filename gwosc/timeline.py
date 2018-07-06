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

from . import api
from .urls import sieve


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
    meta = api.fetch_dataset_json(start, end, host=host)
    duration = end-start

    epochs = []

    for type_ in meta:
        for epoch, metadata in meta[type_].items():
            if epoch == 'tenyear':  # tenyear doesn't work with json API
                continue

            # filter on detector
            if detector not in metadata['detectors']:
                continue

            # get dataset segment
            if type_ == 'events':
                segment = _event_segment(epoch, host=host, detector=detector)
            elif type_ == 'runs':
                segment = metadata['GPSstart'], metadata['GPSend']
            else:
                raise ValueError(
                    "Unrecognised dataset type {!r}".format(type_))

            # compare with request
            overlap = min(end, segment[1]) - max(start, segment[0])
            epochs.append((epoch, duration-overlap))

    if not epochs:
        raise ValueError(
            "No datasets found matching [{}, {})".format(start, end))

    return sorted(epochs, key=itemgetter(1, 0))[0][0]


def _event_segment(event, host=api.DEFAULT_URL, **match):
    jdata = api.fetch_event_json(event, host=host)
    seg = None
    for fmeta in sieve(jdata['strain'], **match):
        start = fmeta['GPSstart']
        end = start + fmeta['duration']
        if seg is None:  # first segment
            seg = (start, end)
            continue
        seg = min(start, seg[0]), max(end, seg[1])

    # fail on no match
    if seg is None:
        raise ValueError("No files matched for event {}".format(event))

    return seg
