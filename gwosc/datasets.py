# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2018-2021)
# SPDX-License-Identifier: MIT

"""
`gwosc.datasets` includes functions to query for available datasets.

To search for all available datasets:

>>> from gwosc import datasets
>>> datasets.find_datasets()
['GW150914', 'GW151226', 'GW170104', 'GW170608', 'GW170814', 'GW170817', 'LVT151012', 'O1', 'S5', 'S6']
>>> datasets.find_datasets(detector='V1')
['GW170814', 'GW170817']
>>> datasets.find_datasets(type='run')
['O1', 'S5', 'S6']

To query for the GPS time of an event dataset (or vice-versa):

>>> datasets.event_gps('GW170817')
1187008882.43
>>> datasets.event_at_gps(1187008882)
'GW170817'

Similar queries are available for observing run datasets:

>>> datasets.run_segment('O1')
(1126051217, 1137254417)
>>> datasets.run_at_gps(1135136350)  # event_gps('GW151226')
'O1'
"""  # noqa: E501

import re
import warnings

from . import (
    api,
    urls,
    utils,
)

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'

_IGNORE = {
    "tenyear",
    "history",
    "oldhistory",
}


def _match_dataset(targetdetector, detectors, targetsegment, segment):
    """Returns `True` if the dataset metadata matches the target
    """
    if targetdetector not in set(detectors) | {None}:
        return False
    if targetsegment is None or utils.segments_overlap(
            targetsegment, segment):
        return True


def _run_datasets(detector=None, segment=None, host=api.DEFAULT_URL):
    meta = api.fetch_dataset_json(0, api._MAX_GPS, host=host)["runs"]
    for epoch, metadata in meta.items():
        # ignore tenyear, etc...
        if epoch in _IGNORE:
            continue
        rundets = set(metadata["detectors"])
        runseg = (metadata['GPSstart'], metadata['GPSend'])
        if _match_dataset(detector, rundets, segment, runseg):
            yield epoch


def _catalog_datasets(host=api.DEFAULT_URL):
    yield from api.fetch_cataloglist_json(host=host).keys()


def _match_event_dataset(
        dataset,
        catalog=None,
        version=None,
        detector=None,
        segment=None,
        host=api.DEFAULT_URL,
):
    # get strain file list (matching catalog and version)
    full = bool(detector or segment)
    try:
        meta = _event_metadata(
            dataset,
            catalog=catalog,
            version=version,
            full=full,
            host=host,
        )
    except ValueError:  # no dataset matching catalog and/or version
        return False

    if not full:  # detector=None, segment=None
        return True
    try:
        strain = meta["strain"]
    except KeyError:  # pragma: no cover
        # no strain file list for this dataset
        return False

    # match detector
    if detector not in {None} | {u["detector"] for u in strain}:
        return False

    # match segment
    if segment is None:
        return True
    if not strain:
        return False
    eseg = utils.strain_extent(urls.sieve(strain, detector=detector))
    return utils.segments_overlap(segment, eseg)


def _event_datasets(
        detector=None,
        segment=None,
        catalog=None,
        version=None,
        host=api.DEFAULT_URL,
):
    full = detector is not None or segment is not None
    events = {}
    for dset, meta in api.fetch_allevents_json(
        host=host,
        full=full,
    )["events"].items():
        if _match_event_dataset(
            dset,
            detector=detector,
            segment=segment,
            catalog=catalog,
            version=version,
            host=host,
        ):
            events[dset] = meta

    def _rank_catalog(x):
        cat = x["catalog.shortName"].lower()
        if "confident" in cat:
            return 1
        for word in ("marginal", "preliminary"):
            if word in cat:
                return 10
        return 5

    def _gps_distance(x):
        gps = x["GPS"]
        if not segment:
            return 0
        return int(abs(segment[0] - gps))

    for dset, _ in sorted(
        events.items(),
        key=lambda x: (
            _gps_distance(x[1]),
            _rank_catalog(x[1]),
            -x[1]["version"],
        ),
    ):
        yield dset


def _iter_datasets(
        detector=None,
        type=None,
        segment=None,
        catalog=None,
        version=None,
        match=None,
        host=api.DEFAULT_URL,
):
    # get queries
    type = str(type).rstrip("s").lower()
    needruns = type in {"none", "run"}
    needcatalogs = type in {"none", "catalog"}
    needevents = type in {"none", "event"}

    # warn about event-only keywords when not querying for events
    if not needevents:
        for key, value in dict(catalog=catalog, version=version).items():
            if value is not None:
                warnings.warn(
                    "the '{}' keyword is only relevant when querying "
                    "for event datasets, it will be ignored now".format(key),
                )

    if match:
        reg = re.compile(match)

    def _yield_matches(iter_):
        for x in iter_:
            if not match or reg.search(x):
                yield x

    # search for events and datasets
    for needthis, collection in (
        (needruns, _run_datasets(
            detector=detector,
            host=host,
            segment=segment,
        )),
        (needcatalogs, _catalog_datasets(
            host=host,
        )),
        (needevents, _event_datasets(
            detector=detector,
            segment=segment,
            host=host,
            version=version,
            catalog=catalog,
        )),
    ):
        if not needthis:
            continue
        yield from _yield_matches(collection)


def find_datasets(
        detector=None,
        type=None,
        segment=None,
        match=None,
        catalog=None,
        version=None,
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
        datasets will match if they overlap at any point; this is
        not used to filter catalogs

    match : `str`, optional
        regular expression string against which to match datasets

    host : `str`, optional
        the URL of the GWOSC host to query, defaults to
        https://www.gw-openscience.org

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
    return sorted(list(_iter_datasets(
        detector=detector,
        type=type,
        segment=segment,
        catalog=catalog,
        version=version,
        match=match,
        host=host,
    )))


# -- event utilities ----------------------------------------------------------

def _event_metadata(
        event,
        catalog=None,
        version=None,
        full=True,
        host=api.DEFAULT_URL,
):
    return list(api._fetch_allevents_event_json(
        event,
        catalog=catalog,
        version=version,
        full=full,
        host=host,
    )["events"].values())[0]


def event_gps(event, catalog=None, version=None, host=api.DEFAULT_URL):
    """Returns the GPS time of an open-data event

    Parameters
    ----------
    event : `str`
        the name of the event to query

    catalog : `str`, optional
        name of catalogue that hosts this event

    version : `int`, `None`, optional
        the version of the data release to use,
        defaults to the highest available version

    host : `str`, optional
        the URL of the GWOSC host to query, defaults to
        https://www.gw-openscience.org

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
    return _event_metadata(
        event,
        catalog=catalog,
        version=version,
        full=False,
        host=host,
    )['GPS']


def event_segment(
        event,
        detector=None,
        catalog=None,
        version=None,
        host=api.DEFAULT_URL,
):
    """Returns the GPS ``[start, stop)`` interval covered by an event dataset

    Parameters
    ----------
    event : `str`
        the name of the event

    detector : `str`, optional
        prefix of GW detector

    catalog : `str`, optional
        name of catalogue that hosts this event

    version : `int`, `None`, optional
        the version of the data release to use,
        defaults to the highest available version

    host : `str`, optional
        the URL of the GWOSC host to query, defaults to
        https://www.gw-openscience.org

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
    data = _event_metadata(
        event,
        catalog=catalog,
        version=version,
        full=True,
        host=host,
    )

    if not data["strain"]:  # pragma: no cover
        raise ValueError(
            "event '{}' has no strain files".format(event),
        )

    return utils.strain_extent(
        urls.sieve(data["strain"], detector=detector),
    )


def event_at_gps(gps, host=api.DEFAULT_URL, tol=1):
    """Returns the name of the open-data event matching the GPS time

    This function will return the first event for which
    ``|eventgps - gps| < = tol``.

    Parameters
    ----------
    gps : `float`
        The GPS time to locate

    host : `str`, optional
        the URL of the GWOSC host to query, defaults to
        https://www.gw-openscience.org

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
    for meta in api.fetch_allevents_json(host=host)["events"].values():
        egps = meta['GPS']
        if abs(egps - gps) <= tol:
            return meta["commonName"]
    raise ValueError("no event found within {0} seconds of {1}".format(
        tol, gps))


def event_detectors(event, catalog=None, version=None, host=api.DEFAULT_URL):
    """Returns the `set` of detectors that observed an event

    Parameters
    ----------
    event : `str`
        the name of the event to query

    host : `str`, optional
        the URL of the GWOSC host to query, defaults to
        https://www.gw-openscience.org

    version : `int`, `None`, optional
        the version of the data release to use,
        defaults to the highest available version

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
    data = _event_metadata(
        event,
        catalog=catalog,
        version=version,
        full=True,
        host=host,
    )
    return set(u["detector"] for u in data["strain"])


# -- run utilities ------------------------------------------------------------

def run_segment(run, host=api.DEFAULT_URL):
    """Returns the GPS ``[start, stop)`` interval covered by a run dataset

    Parameters
    ----------
    run : `str`
        the name of the run dataset to query

    host : `str`, optional
        the URL of the GWOSC host to query, defaults to
        https://www.gw-openscience.org

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
        meta = api.fetch_dataset_json(0, api._MAX_GPS, host=host)['runs'][run]
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
        the URL of the GWOSC host to query, defaults to
        https://www.gw-openscience.org

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
            0, api._MAX_GPS, host=host)['runs'].items():
        if run in _IGNORE:
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
        the URL of the GWOSC host to query

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
        if dataset in find_datasets(type=type_, host=host):
            return type_
    raise ValueError(
        "failed to determine type for dataset {0!r}".format(dataset),
    )
