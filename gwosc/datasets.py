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

"""Functions for getting information about available datasets

Note: each of these methods deliberately excludes the 'tenyear' dataset.
"""

from six import raise_from

from . import api

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'


def find_datasets(detector=None, type=None, host=api.DEFAULT_URL):
    """Find datasets available on the given GW open science host

    Parameters
    ----------
    detector : `str`, optional
        prefix of GW detector

    type : `str`, optional
        type of datasets to restrict, one of ``'run'`` or ``'event'``

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    Returns
    -------
    datasets : `list` of `str`
        the names of all matched datasets, possibly empty

    Examples
    --------
    (Correct as of 2018-03-14)

    >>> from gwosc.datasets import find_datasets
    >>> find_datasets()
    ['GW150914', 'GW151226', 'GW170104', 'GW170608', 'GW170814', 'GW170817',
     'LVT151012', 'O1', 'S5', 'S6']
    >>> find_datasets(detector='V1')
    ['GW170814', 'GW170817']
    >>> find_datasets(type='event')
    ['GW150914', 'GW151226', 'GW170104', 'GW170608', 'GW170814', 'GW170817',
     'LVT151012']
    """
    # format type
    if type not in [None, 'run', 'event']:
        raise ValueError('unrecognised type {!r}, select one of \'run\', '
                         '\'event\''.format(type))
    if type and not type.endswith('s'):
        type += 's'

    # search
    meta = api.fetch_dataset_json(0, api.MAX_GPS, host=host)
    names = []
    for type_ in meta:
        if type and type_ != type:
            continue
        for epoch, metadata in meta[type_].items():
            if epoch == 'tenyear':
                continue
            if detector is None or detector in metadata['detectors']:
                names.append(epoch)
    return sorted(names)


def event_gps(event, host=api.DEFAULT_URL):
    """Returns the GPS time of an open-data event

    Parameters
    ----------
    event : `str`
        the name of the event to query

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    Returns
    -------
    gps : `float`
        the GPS time of this event

    Examples
    --------
    >>> from gwosc.datasets import event_gps
    >>> event_gps('GW170817')
    1187008882.43
    >>> event_gps('GW123456')
    ValueError: no event dataset found for 'GW123456'
    """
    try:
        return api.fetch_event_json(event, host=host)['GPS']
    except ValueError as exc:
        raise_from(
            ValueError('no event dataset found for {0!r}'.format(event)),
            exc)


def event_at_gps(gps, host=api.DEFAULT_URL, tol=1):
    """Returns the name of the open-data event matching the GPS time

    This function will return the first event for which
    ``|eventgps - gps| < = tol``.

    Parameters
    ----------
    gps : `float`
        The GPS time to locate

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    tol : `float`, optional
        the search window (in seconds), default: ``1``

    Returns
    -------
    event : `str`
        the name of the matched event

    Raises
    -------
    ValueError
        if no events are found matching the GPS time

    Examples
    --------
    >>> from gwosc.datasets import event_at_gps
    >>> event_at_gps(1187008882)
    'GW170817'
    >>> event_at_gps(1187008882, tol=.1)
    ValueError: no event found within 0.1 seconds of 1187008882
    """
    for event, meta in api.fetch_dataset_json(
            0, api.MAX_GPS, host=host)['events'].items():
        egps = meta['GPStime']
        if abs(egps - gps) <= tol:
            return event
    raise ValueError("no event found within {0} seconds of {1}".format(
        tol, gps))


def run_segment(run, host=api.DEFAULT_URL):
    """Returns the GPS time of an open-data event

    Parameters
    ----------
    event : `str`
        the name of the event to query

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    Returns
    -------
    gps : `float`
        the GPS time of this event

    Examples
    --------
    >>> from gwosc.datasets import run_segment
    >>> run_segment('O1')
    (1126051217, 1137254417)
    >>> run_segment('Oh dear')
    ValueError: no run dataset found for 'Oh dear'
    """
    try:
        meta = api.fetch_dataset_json(0, api.MAX_GPS, host=host)['runs'][run]
    except KeyError as exc:
        raise ValueError('no run dataset found for {!r}'.format(exc.args[0]))
    return (meta['GPSstart'], meta['GPSend'])


def run_at_gps(gps, host=api.DEFAULT_URL):
    """Returns the name of the open-data event matching the GPS time

    This function will return the first event for which
    ``start <= gps < end``

    Parameters
    ----------
    gps : `float`
        The GPS time to locate

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    Returns
    -------
    run : `str`
        the name of the matched observing run

    Raises
    -------
    ValueError
        if no datasets are found matching the GPS time

    Examples
    --------
    >>> from gwosc.datasets import run_at_gps
    >>> run_at_gps(1135136350)
    'O1'
    >>> run_at_gps(0)
    ValueError: no run dataset found containing GPS 0
    """
    for run, meta in api.fetch_dataset_json(
            0, api.MAX_GPS, host=host)['runs'].items():
        if run == 'tenyear':
            continue
        start, end = meta['GPSstart'], meta['GPSend']
        if start <= gps < end:
            return run
    raise ValueError("no run dataset found containing GPS {0}".format(gps))
