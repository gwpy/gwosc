# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2018-2021)
# SPDX-License-Identifier: MIT

"""
:mod:`gwosc.api` provides the low-level interface functions
that handle direct requests to the GWOSC host.
"""

import logging
import os

import requests

logger = logging.getLogger("gwosc.api")
_loghandler = logging.StreamHandler()
_loghandler.setFormatter(
    logging.Formatter(logging.BASIC_FORMAT),
)
logger.addHandler(_loghandler)
logger.setLevel(int(os.getenv("GWOSC_LOG_LEVEL", logging.NOTSET)))

_MAX_GPS = 99999999999

#: The default GWOSC host URL
DEFAULT_URL = "https://www.gw-openscience.org"

#: Cache of downloaded blobs
JSON_CACHE = {}


# -- JSON handling ------------------------------------------------------------

def fetch_json(url, **kwargs):
    """Fetch JSON data from a remote URL

    Parameters
    ----------
    url : `str`
        the remote URL to fetch

    **kwargs
        other keyword arguments are passed directly to :func:`requests.get`

    Returns
    ------
    data : `dict` or `list`
        the data fetched from ``url`` as parsed by
        :meth:`requests.Response.json`

    See also
    --------
    json.loads
        for details of the JSON parsing
    """
    try:
        return JSON_CACHE[url]
    except KeyError:
        logger.debug("fetching {}".format(url))
        resp = requests.get(url, **kwargs)
        try:
            return JSON_CACHE.setdefault(
                url,
                resp.json(),
            )
        except ValueError as exc:
            exc.args = ("Failed to parse GWOSC JSON from %r: %s"
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
        the URL of the GWOSC host to query, defaults to
        https://www.gw-openscience.org

    Returns
    -------
    data : `dict` or `list`
        the JSON data retrieved from GWOSC and returned by `json.loads`
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
        the URL of the GWOSC host to query, defaults to
        https://www.gw-openscience.org

    Returns
    -------
    data : `dict` or `list`
        the JSON data retrieved from GWOSC and returned by `json.loads`
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
        :meth:`requests.Response.json`
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
        the URL of the GWOSC host to query, defaults to
        https://www.gw-openscience.org

    Returns
    -------
    data : `dict` or `list`
        the JSON data retrieved from GWOSC and returnend by
        :meth:`requests.Response.json`
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
        the URL of the GWOSC host to query, defaults to gw-openscience.org

    Returns
    -------
    data : `dict` or `list`
        the JSON data retrieved from GWOSC and returned by
        :meth:`requests.Response.json`
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

    def _match(keyvalue):
        dset, metadata = keyvalue
        if event not in {
            dset,
            metadata["commonName"],  # full name
            metadata["commonName"].split("_", 1)[0],  # GWYYMMDD prefix
        }:
            return
        if version is not None and metadata["version"] != version:
            return
        if catalog is not None and metadata["catalog.shortName"] != catalog:
            return
        return True

    matched = list(filter(_match, allevents.items()))
    names = set(x[1]["commonName"] for x in matched)
    if matched and len(names) == 1:
        key, meta = sorted(matched, key=lambda x: x[1]["version"])[-1]
        return {"events": {key: meta}}

    # raise error with the right message
    if len(names) > 1:
        raise ValueError(
            "multiple events matched for {!r}: '{}'".format(
                event,
                "', '".join(names),
            ),
        )
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
        the URL of the GWOSC host to query, defaults to
        https://www.gw-openscience.org

    Returns
    -------
    data : `dict` or `list`
        the JSON data retrieved from GWOSC and returned by `json.loads`
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
        the URL of the GWOSC host to query, defaults to
        https://www.gw-openscience.org

    Returns
    -------
    json
        the JSON data retrieved from GWOSC and returnend by
        :meth:`requests.Response.json`
    """
    return fetch_json(_legacy_catalog_url(catalog, host=host))
