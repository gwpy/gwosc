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

import multiprocessing.dummy
from operator import itemgetter

from six import raise_from
from six.moves.urllib.error import URLError

from . import (api, utils, catalog as gwosc_catalog)

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'

IGNORE = {
    "tenyear",
    "history",
}
CATALOGS = [
    "GWTC-1-confident",
    "GWTC-1-marginal",
]


def _match_dataset(targetdetector, detectors, targetsegment, segment):
    """Returns `True` if the dataset metadata matches the target
    """
    if targetdetector not in set(detectors) | {None}:
        return False
    if targetsegment is None or utils.segments_overlap(
            targetsegment, segment):
        return True


def _run_datasets(detector=None, segment=None, host=api.DEFAULT_URL):
    meta = api.fetch_dataset_json(0, api.MAX_GPS, host=host)["runs"]
    for epoch, metadata in meta.items():
        # ignore tenyear, etc...
        if epoch in IGNORE:
            continue
        if _match_dataset(
                detector,
                metadata['detectors'],
                segment,
                (metadata['GPSstart'], metadata['GPSend']),
        ):
            yield epoch


def find_datasets(
        detector=None,
        type=None,
        segment=None,
        host=api.DEFAULT_URL,
):
    """Find datasets available on the given GW open science host

    Parameters
    ----------
    detector : `str`, optional
        prefix of GW detector

    type : `str`, optional
        type of datasets to restrict, one of ``'run'``, ``'event'``, or
        ``'catalog'``

    segment : 2-`tuple` of `int`, `None`, optional
        a GPS ``[start, stop)`` interval to restrict matches to;
        datasets will match if they overlap at any point

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
    # get queries
    type = str(type).rstrip("s").lower()
    needruns = type in {"none", "run"}
    needcatalogs = type in {"none", "catalog"}
    needevents = type in {"none", "event"}

    names = set()

    # search for events and datasets
    if needruns:
        names.update(_run_datasets(
            detector=detector,
            host=host,
            segment=segment,
        ))

    # if we're only search for catalogs, unset other kwargs so that
    # _catalog_datasets doesn't use it (it's slow)
    if not needevents:
        detector = None
        segment = None

    # search for catalogs and catalog entries
    if needcatalogs or needevents:
        for catalog in CATALOGS:
            try:
                events = gwosc_catalog.events(
                    catalog,
                    detector=detector,
                    segment=segment,
                    host=host,
                )
            except (URLError, ValueError):  # catalog not found
                continue
            # record catalog itself
            if needcatalogs:
                names.add(catalog)
            # record events
            if needevents:
                names.update(events)

    return sorted(names)


# -- event utilities ----------------------------------------------------------

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
        return api.fetch_catalog_event_json(event, host=host)['GPS']
    except ValueError as exc:
        raise_from(
            ValueError('no event dataset found for {0!r}'.format(event)),
            exc,
        )


def event_segment(event, detector=None, version=None, host=api.DEFAULT_URL):
    """Returns the GPS ``[start, stop)`` interval covered by an event dataset

    Parameters
    ----------
    event : `str`
        the name of the event

    detector : `str`, optional
        prefix of GW detector

    version : `int`, `None`, optional
        the version of the data release to use,
        defaults to the highest available version

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    Returns
    -------
    start, end : `int`
        the GPS ``[start, end)`` interval covered by this run dataset

    Examples
    --------
    >>> from gwosc.datasets import event_segment
    >>> event_segment("GW150914")
    segment(1126257415, 1126261511)
    """
    data = api.fetch_catalog_event_json(event, host=host, version=version)
    urls = [u["url"] for u in data["strain"] if
            detector in {u["detector"], None}]
    return utils.urllist_extent(urls)


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


def event_detectors(event, host=api.DEFAULT_URL, version=None):
    """Returns the `set` of detectors that observed an event

    Parameters
    ----------
    event : `str`
        the name of the event to query

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    version : `int`, `None`, optional
        the data-release version to use, defaults to the highest available
        version

    Returns
    -------
    detectors : `set`
        the set of detectors for which data file URLs are included in
        the data release

    Examples
    --------
    >>> from gwosc.datasets import event_detectors
    >>> event_detectors("GW150914")
    {'H1', 'L1'}
    """
    data = api.fetch_catalog_event_json(event, host=host, version=version)
    return set(url['detector'] for url in data['strain'])


# -- run utilities ------------------------------------------------------------

def run_segment(run, host=api.DEFAULT_URL):
    """Returns the GPS ``[start, stop)`` interval covered by a run dataset

    Parameters
    ----------
    event : `str`
        the name of the event to query

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    Returns
    -------
    start, end : `int`
        the GPS ``[start, end)`` interval covered by this run dataset

    Examples
    --------
    >>> from gwosc.datasets import run_segment
    >>> run_segment('O1')
    segment(1126051217, 1137254417)
    >>> run_segment('Oh dear')
    ValueError: no run dataset found for 'Oh dear'
    """
    try:
        meta = api.fetch_dataset_json(0, api.MAX_GPS, host=host)['runs'][run]
    except KeyError as exc:
        raise ValueError('no run dataset found for {!r}'.format(exc.args[0]))
    return meta['GPSstart'], meta['GPSend']


def run_at_gps(gps, host=api.DEFAULT_URL):
    """Returns the name of the open-data run dataset matching the GPS time

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
        if run in IGNORE:
            continue
        start, end = meta['GPSstart'], meta['GPSend']
        if start <= gps < end:
            return run
    raise ValueError("no run dataset found containing GPS {0}".format(gps))


def dataset_type(dataset, host=api.DEFAULT_URL):
    """Returns the type of the named dataset

    Parameters
    ----------
    dataset : `str`
        The name of the dataset to match

    host : `str`, optional
        the URL of the LOSC host to query

    Returns
    -------
    type : `str`
        the type of the dataset, one of 'run', 'event', or 'catalog'

    Raises
    -------
    ValueError
        if this dataset cannot be matched

    Examples
    --------
    >>> from gwosc.datasets import dataset_type
    >>> dataset_type('O1')
    'run'
    """
    for type_ in ("run", "catalog", "event"):
        if dataset in find_datasets(type=type_):
            return type_
    raise ValueError(
        "failed to determine type for dataset {0!r}".format(dataset),
    )
