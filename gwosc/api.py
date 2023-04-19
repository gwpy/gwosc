# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2018-2021)
# SPDX-License-Identifier: MIT

"""
:mod:`gwosc.api` provides the low-level interface functions
that handle direct requests to the GWOSC host.
"""

import logging
import os
import re
from urllib.parse import urlencode
from . import __version__

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
DEFAULT_URL = "https://gwosc.org"

#: Cache of downloaded blobs
JSON_CACHE = {}

_ALLOWED_OPS = set((">=", "=>", "<=", "=<"))

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
        client_headers = {"User-Agent": f"python-gwosc/{__version__}"}
        resp = requests.get(url, headers=client_headers, **kwargs)
        resp.raise_for_status()
        return JSON_CACHE.setdefault(
            url,
            resp.json(),
        )


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
        https://gwosc.org

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
        https://gwosc.org

    Returns
    -------
    data : `dict` or `list`
        the JSON data retrieved from GWOSC and returned by `json.loads`
    """
    return fetch_json(_run_url(run, detector, gpsstart, gpsend, host=host))


# -- EventAPI catalogs -------------------------------------------------------

def _allowed_params_url(host=DEFAULT_URL):
    return "{}/eventapi/json/query/params/".format(host)


def fetch_allowed_params_json(host=DEFAULT_URL):
    return fetch_json(_allowed_params_url(host=host))


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
        https://gwosc.org

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
        the URL of the GWOSC host to query, defaults to https://gwosc.org

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

    # match datasets
    matched = list(filter(_match, allevents.items()))
    names = set(x[1]["commonName"] for x in matched)

    # one dataset has an exact name match, so discard everything else
    if event in names:
        matched = [x for x in matched if x[1]["commonName"] == event]
        names = set(x[1]["commonName"] for x in matched)

    # we have a winner!
    if len(names) == 1:
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


def _parse_two_ops(compiled_m, host=DEFAULT_URL):
    allowed_params = fetch_allowed_params_json(host=host)
    md = compiled_m.groupdict()
    op1, op2 = md["op1"], md["op2"]
    if not set((op1, op2)).issubset(_ALLOWED_OPS):
        raise ValueError(
            "Could not parse select string.\n"
            "Unknown operators."
        )
    param, val1, val2 = md["param"], md["val1"], md["val2"]
    if param not in allowed_params:
        raise ValueError(
            "Could not parse select string.\n"
            f"Unrecognized parameter: {param}.\n"
            f"Use one of:\n{allowed_params}"
        )
    queries = []
    if ">" in op1:
        queries.append((f"max-{param}", val1))
    if "<" in op1:
        queries.append((f"min-{param}", val1))
    if ">" in op2:
        queries.append((f"min-{param}", val2))
    if "<" in op2:
        queries.append((f"max-{param}", val2))
    return queries


def _parse_one_op(compiled_m, host=DEFAULT_URL):
    allowed_params = fetch_allowed_params_json(host=host)
    md = compiled_m.groupdict()
    op = md["op"]
    if not set((op,)).issubset(_ALLOWED_OPS):
        raise ValueError(
            "Could not parse select string.\n"
            "Unknown operator."
        )
    param, val = md["param"], md["val"]
    if param not in allowed_params:
        raise ValueError(
            f"Could not parse select string.\n"
            f"Unrecognized parameter: {param}.\n"
            f"Use one of:\n{allowed_params}"
        )
    queries = []
    if ">" in op:
        queries.append((f"min-{param}", val))
    if "<" in op:
        queries.append((f"max-{param}", val))
    return queries


def _select_to_query(select, host=DEFAULT_URL):
    """Parse select string and translate into URL GET parameters"""

    # Captures strings of the form `1.44 <= param <= 5.0`
    two_ops = re.compile(
        r"^\s*(?P<val1>[\d.+-eE]+)\s*(?P<op1>[<>=]{2})\s*(?P<param>[\w-]+)"
        r"\s*(?P<op2>[<>=]+)\s*(?P<val2>[\d.+-eE]+)\s*$"
    )
    # Captures strings of the form `param <= 5.0`
    one_op = re.compile(
        r"^\s*(?P<param>[\w-]+)\s*(?P<op>[<>=]{2})\s*(?P<val>[\d.+-eE]+)\s*$"
    )

    queries = []
    for s in select:
        for regex, _parse in (
            (one_op, _parse_one_op),
            (two_ops, _parse_two_ops),
        ):
            m = regex.match(s)
            if m is not None:
                queries.extend(_parse(m, host=host))
                break
        else:
            raise ValueError(f"Could not parse select string: {s}")
    return urlencode(queries)


def _query_events_url(select, host=DEFAULT_URL):
    return "{}/eventapi/json/query/show?{}".format(
        host, _select_to_query(select, host=host)
    )


def fetch_filtered_events_json(select, host=DEFAULT_URL):
    """"Return the JSON metadata for the events constrained by select

    Parameters
    ----------
    select : `list-like`
        a list of range constrains for the events.
        All ranges should have inclusive ends (<= and >= operators).

    host : `str`, optional
        the URL of the GWOSC host to query, defaults to
        https://gwosc.org

    Returns
    -------
    data : `dict` or `list`
        the JSON data retrieved from GWOSC and returnend by
        :meth:`requests.Response.json`

    Example
    -------
    >>> fetch_filtered_events_json(
    ...     select=[
    ...         "mass-1-source <= 5",
    ...         "mass-2-source =< 10",
    ...         "10 <= luminosity-distance <= 100",
    ...     ]
    ... )
    """
    return fetch_json(_query_events_url(select, host=host))


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
        https://gwosc.org

    Returns
    -------
    data : `dict` or `list`
        the JSON data retrieved from GWOSC and returned by `json.loads`
    """
    return fetch_json(
        _event_url(event, catalog=catalog, version=version, host=host),
    )
