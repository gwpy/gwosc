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
:mod:`gwosc.api` provides the low-level interface functions
that handle direct requests to the GWOSC host.
"""

import contextlib
import json
import logging
import os
import re
from urllib.request import urlopen

logger = logging.getLogger("gwosc.api")
_loghandler = logging.StreamHandler()
_loghandler.setFormatter(
    logging.Formatter(logging.BASIC_FORMAT),
)
logger.addHandler(_loghandler)
logger.setLevel(int(os.getenv("GWOSC_LOG_LEVEL", logging.NOTSET)))

_MAX_GPS = 99999999999
_VERSIONED_EVENT_REGEX = re.compile(r"_[RV]\d+\Z")

#: The default GWOSC host URL
DEFAULT_URL = "https://www.gw-openscience.org"

#: Cache of downloaded blobs
JSON_CACHE = {}


# -- JSON handling ------------------------------------------------------------

def fetch_json(url):
    """Fetch JSON data from a remote URL

    Parameters
    ----------
    url : `str`
        the remote URL to fetch

    Returns
    ------
    data : `dict` or `list`
        the data fetched from ``url`` as parsed by :func:`json.loads`

    See also
    --------
    json.loads
        for details of the JSON parsing
    """
    try:
        return JSON_CACHE[url]
    except KeyError:
        logger.debug("fetching {}".format(url))
        with contextlib.closing(urlopen(url)) as response:
            data = response.read()
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            try:
                return JSON_CACHE.setdefault(
                    url,
                    json.loads(data),
                )
            except ValueError as exc:
                exc.args = ("Failed to parse LOSC JSON from %r: %s"
                            % (url, str(exc)),)
                raise


# -- Run datasets -------------------------------------------------------------

def _dataset_url(start, end, host=DEFAULT_URL):
    return "{}/archive/{:d}/{:d}/json/".format(host, start, end)


def fetch_dataset_json(gpsstart, gpsend, host=DEFAULT_URL):
    """Returns the JSON metadata for all datasets matching the GPS interval

    Parameters
    ----------
    gpsstart : `int`
        the GPS start of the desired interval

    gpsend : `int`
        the GPS end of the desired interval

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    Returns
    -------
    data : `dict` or `list`
        the JSON data retrieved from LOSC and returned by `json.loads`
    """
    return fetch_json(_dataset_url(gpsstart, gpsend, host=host))


def _run_url(run, detector, start, end, host=DEFAULT_URL):
    return "{}/archive/links/{}/{}/{:d}/{:d}/json/".format(
        host, run, detector, start, end,
    )


def fetch_run_json(run, detector, gpsstart=0, gpsend=_MAX_GPS,
                   host=DEFAULT_URL):
    """Returns the JSON metadata for the given science run parameters

    Parameters
    ----------
    run : `str`
        the name of the science run, e.g. ``'O1'``

    detector : `str`
        the prefix of the GW detector, e.g. ``'L1'``

    gpsstart : `int`
        the GPS start of the desired interval

    gpsend : `int`
        the GPS end of the desired interval

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    Returns
    -------
    data : `dict` or `list`
        the JSON data retrieved from LOSC and returned by `json.loads`
    """
    return fetch_json(_run_url(run, detector, gpsstart, gpsend, host=host))


# -- EventAPI catalogs -------------------------------------------------------

def _eventapi_url(full=False, host=DEFAULT_URL):
    j = "jsonfull" if full else "json"
    return "{}/eventapi/{}/".format(host, j)


def fetch_cataloglist_json(host=DEFAULT_URL):
    """Returns the JSON metadata for the catalogue list.

    Parameters
    ----------
    host : `str`, optional
        the URL of the GWOSC host to query

    Returns
    -------
    data : `dict` or `list`
        the JSON data retrieved from GWOSC and returned by
        :func:`json.loads`
    """
    return fetch_json(_eventapi_url(host=host))


def _catalog_url(catalog, host=DEFAULT_URL):
    return "{}{}/".format(_eventapi_url(host=host), catalog)


def fetch_catalog_json(catalog, host=DEFAULT_URL):
    """"Returns the JSON metadata for the given catalogue

    Parameters
    ----------
    catalog : `str`
        the name of the event catalog, e.g. `GWTC-1-confident`

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    Returns
    -------
    data : `dict` or `list`
        the JSON data retrieved from GWOSC and returnend by
        :func:`json.loads`
    """
    return fetch_json(_catalog_url(catalog, host=host))


# -- EventAPI events ---------------------------------------------------------

def _allevents_url(full=False, host=DEFAULT_URL):
    return "{}allevents/".format(_eventapi_url(full=full, host=host))


def _has_jsonfull_allevents(host=DEFAULT_URL):
    return _allevents_url(full=True, host=host) in JSON_CACHE


def fetch_allevents_json(full=False, host=DEFAULT_URL):
    """"Returns the JSON metadata for the allevents API

    Parameters
    ----------
    host : `str`, optional
        the URL of the LOSC host to query, defaults to gw-openscience.org

    Returns
    -------
    data : `dict` or `list`
        the JSON data retrieved from GWOSC and returned by
        :func:`json.loads`
    """
    if full is None and _has_jsonfull_allevents(host=host):
        return fetch_json(_allevents_url(full=True, host=host))
    return fetch_json(_allevents_url(full=full, host=host))


def _fetch_allevents_event_json(
        event,
        catalog=None,
        version=None,
        full=False,
        host=DEFAULT_URL,
):
    """Returns the JSON metadata from the allevents view for a specific event

    The raw JSON data are packaged to look the same as if they came from
    a full event API query, i.e. nested under `'events`'.
    """
    allevents = fetch_allevents_json(full=full, host=host)["events"]
    matched = []
    for dset, metadata in allevents.items():
        name = metadata["commonName"]
        if event not in {dset, name}:
            continue
        thisversion = metadata["version"]
        if version is not None and thisversion != version:
            continue
        thiscatalog = metadata["catalog.shortName"]
        if catalog is not None and thiscatalog != catalog:
            continue
        matched.append((dset, thisversion, metadata))
    if matched:
        key, _, meta = sorted(matched, key=lambda x: x[1])[-1]
        return {"events": {key: meta}}

    # raise error with the right message
    msg = "failed to identify {} for event '{}'"
    if catalog is None:
        msg = msg.format("catalog", event)
        if version is not None:
            msg += " at version {}".format(version)
        raise ValueError(msg)
    msg = msg.format("version", event)
    if catalog is not None:
        msg += " in catalog '{}'".format(catalog)
    raise ValueError(msg)


def _event_url(
        event,
        catalog=None,
        version=None,
        host=DEFAULT_URL,
):
    return list(_fetch_allevents_event_json(
        event,
        catalog=catalog,
        version=version,
        full=None,
        host=host,
    )["events"].values())[0]["jsonurl"]


def fetch_event_json(
        event,
        catalog=None,
        version=None,
        host=DEFAULT_URL,
):
    """Returns the JSON metadata for the given event.

    By default, this function queries across all catalogs and all data-release
    versions, returning the highest available version, unless the
    ``version`` and/or ``catalog`` keywords are specified.

    Parameters
    ----------
    event : `str`
        the name of the event to query

    catalog : `str`, optional
        name of catalogue that hosts this event

    version : `int`, `None`, optional
        restrict query to a given data-release version

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    Returns
    -------
    data : `dict` or `list`
        the JSON data retrieved from LOSC and returned by `json.loads`
    """
    return fetch_json(
        _event_url(event, catalog=catalog, version=version, host=host),
    )


# -- legacy

def _legacy_catalog_url(catalog, host=DEFAULT_URL):
    return "{}/catalog/{}/filelist/".format(
        host, catalog,
    )


def fetch_legacy_catalog_json(catalog, host=DEFAULT_URL):
    """"Returns the JSON metadata for the given catalogue

    Parameters
    ----------
    catalog : `str`
        the name of the event catalog, e.g. `GWTC-1-confident`

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    Returns
    -------
    json
        the JSON data retrieved from GWOSC and returnend by
        :func:`json.loads`
    """
    return fetch_json(_legacy_catalog_url(catalog, host=host))
