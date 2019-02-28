# -*- coding: utf-8 -*-
# Copyright Duncan Macleod 2018
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

import contextlib
import json
import re

from six.moves.urllib.request import urlopen
from six.moves.urllib.error import URLError

DEFAULT_URL = "https://www.gw-openscience.org"
MAX_GPS = 99999999999

VERSIONED_EVENT_REGEX = re.compile(r"_[RV]\d+\Z")


# -- JSON handling ------------------------------------------------------------

def fetch_json(url):
    """Fetch JSON data from a remote URL

    Parameters
    ----------
    url : `str`
        the remote URL to fetch

    Returns
    ------
    json : `object`
        the data fetched from ``url`` as parsed by :func:`json.loads`

    See also
    --------
    json.loads
        for details of the JSON parsing

    Examples
    --------
    >>> from gwpy.io.losc import fetch_json
    >>> fetch_json('https://losc.ligo.org/archive/1126257414/1126261510/json/')
    """
    with contextlib.closing(urlopen(url)) as response:
        data = response.read()
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        try:
            return json.loads(data)
        except ValueError as exc:
            exc.args = ("Failed to parse LOSC JSON from %r: %s"
                        % (url, str(exc)),)
            raise


# -- API calls ----------------------------------------------------------------

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
    json
        the JSON data retrieved from LOSC and returned by `json.loads`
    """
    return fetch_json(_dataset_url(gpsstart, gpsend, host=host))


def _event_url(event, host=DEFAULT_URL):
    return "{}/archive/{}/json/".format(host, event)


def fetch_event_json(event, host=DEFAULT_URL):
    """Returns the JSON metadata for the given event

    Parameters
    ----------
    event : `str`
        the name of the event to query

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    Returns
    -------
    json
        the JSON data retrieved from LOSC and returned by `json.loads`
    """
    return fetch_json(_event_url(event, host=host))


def _run_url(run, detector, start, end, host=DEFAULT_URL):
    return "{}/archive/links/{}/{}/{:d}/{:d}/json/".format(
        host, run, detector, start, end,
    )


def fetch_run_json(run, detector, gpsstart=0, gpsend=MAX_GPS,
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
    json
        the JSON data retrieved from LOSC and returned by `json.loads`
    """
    return fetch_json(_run_url(run, detector, gpsstart, gpsend, host=host))


def _catalog_url(catalog, host=DEFAULT_URL):
    return "{}/catalog/{}/filelist/".format(
        host, catalog,
    )


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
    json
        the JSON data retrieved from GWOSC and returnend by
        :func:`json.loads`
    """
    return fetch_json(_catalog_url(catalog, host=host))


def fetch_catalog_event_json(event, version=None, host=DEFAULT_URL):
    """Returns the JSON metadata for the given event in a catalog

    This method queries for all available data-release versions, returning
    the highest available version, unless ``version=<X>`` is specified.

    Parameters
    ----------
    event : `str`
        the name of the event to query

    host : `str`, optional
        the URL of the LOSC host to query, defaults to losc.ligo.org

    version : `int`, `None`, optional
        restrict query to a given data-release version

    Returns
    -------
    json
        the JSON data retrieved from LOSC and returned by `json.loads`
    """
    # if user gave a versioned event (e.g. GW150914_R1), use it directly
    if VERSIONED_EVENT_REGEX.search(event):
        return fetch_event_json(event, host=host)

    # if user specified a version separately, use it
    if version is not None:
        return fetch_event_json("{0}_R{1}".format(event, version), host=host)

    # otherwise find all available versions and return highest
    # its inefficient, but it works..
    versions = _find_catalog_event_versions(event, host=host)
    return fetch_catalog_event_json(event, version=versions[-1], host=host)


def _find_catalog_event_versions(event, host=DEFAULT_URL):
    """List all available versions of a catalogue event
    """
    vers = 1
    found = []
    while True:
        try:
            resp = urlopen(_event_url("{0}_R{1}".format(event, vers),
                                      host=host))
        except URLError:
            break
        else:
            resp.close()
        found.append(vers)
        vers += 1
    if not found:
        raise ValueError("no event datasets found for {!r}".format(event))
    return found
