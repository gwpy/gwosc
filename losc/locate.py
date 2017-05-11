# -*- coding: utf-8 -*-
# Copyright Duncan Macleod 2017
#
# This file is part of LOSC-Python.
#
# LOSC-Python is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LOSC-Python is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LOSC-Python.  If not, see <http://www.gnu.org/licenses/>.

"""Locate files within a given interval on losc.ligo.org
"""

import json

from six.moves.urllib.request import urlopen

from . import utils

__all__ = ['get_urls', 'get_event_urls']
__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'

# default URL
LOSC_URL = 'https://losc.ligo.org'


def read_json(url):
    """Read a JSON file from a remote URL

    Parameters
    ----------
    url : `str`
        a remote (http or https) URL of a JSON file

    Returns
    -------
    jdata : `dict`
        a python representation of the JSON data
    """
    # fetch the URL
    try:
        response = urlopen(url)
    except (IOError, Exception) as e:
        e.args = ("Failed to access LOSC metadata from %r: %s"
                  % (url, str(e)),)
        raise
    # parse the JSON
    data = response.read()
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    try:
        return json.loads(data)
    except ValueError as e:
        e.args = ("Failed to parse LOSC JSON from %r: %s"
                  % (url, str(e)),)
        raise


def parse_file_urls(metadata, detector, sample_rate=4096,
                    format='hdf5', duration=4096):
    """Parse a list of file URLs from a LOSC metadata packet

    Parameters
    ----------
    metadata : `dict`
        a python representation of JSON data

    detector : `str`
        the prefix of the relevant GW detector

    sample_rate : `int`, optional, default : ``4096``
        the sampling rate (Hz) of files you want to find

    format : `str`, optional, default: ``'hdf5'``
        the file format (extension) you want to find

    duration : `int`, optional, default: ``4096``
        the duration of files you want to find

    Returns
    -------
    urls : `list` of `str`
        the list of URLs matching the input parameters
    """
    urls = []
    for fmd in metadata:  # loop over file metadata dicts
        # skip files we don't want
        if (fmd['detector'] != detector or
                fmd['sampling_rate'] != sample_rate or
                fmd['format'] != format or
                fmd['duration'] != duration):
            continue
        urls.append(str(fmd['url']))
    return urls


def get_urls(detector, start, end, host=LOSC_URL,
             sample_rate=4096, format='hdf5'):
    """Fetch the metadata from LOSC regarding a given GPS interval

    Parameters
    ----------
    detector : `str`
        the prefix of the relevant GW detector

    start : `int`
        the GPS start time of your query

    end : `int`
        the GPS end time of your query

    host : `str`, optional
        the URL of the remote LOSC server

    sample_rate : `int`, optional, default : ``4096``
        the sampling rate (Hz) of files you want to find

    format : `str`, optional, default: ``'hdf5'``
        the file format (extension) you want to find

    duration : `int`, optional, default: ``4096``
        the duration of files you want to find

    Returns
    -------
    urls : `list` of `str`
        the list of remote file URLs that contain data matching the
        relevant parameters
    """
    start = int(start)
    end = int(end)

    # step 1: query the interval and parse the json packet
    url = '%s/archive/%d/%d/json/' % (host, start, end)
    md = read_json(url)

    # step 2: parse the list of URLS for each dataset and work out
    #         which one covers the interval
    for dstype in ['events', 'runs']:  # try event datasets first (less files)
        for dataset in md[dstype]:
            # validate IFO is present
            if detector not in md[dstype][dataset]['detectors']:
                continue
            # get metadata for this dataset
            if dstype == 'events':
                url = '%s/archive/%s/json/' % (host, dataset)
            else:
                url = ('%s/archive/links/%s/%s/%d/%d/json/'
                       % (host, dataset, detector, start, end))
            jsonmetadata = read_json(url)
            # get cache and sieve for our segment
            for duration in [32, 4096]:  # try short files for events first
                urls = parse_file_urls(
                    jsonmetadata['strain'], detector, sample_rate=sample_rate,
                    format=format, duration=duration)
                urls = [u for u in urls if
                        utils.segments_overlap(utils.url_segment(u),
                                               (start, end))]
                # if full span covered, return now
                if utils.full_coverage(urls, (start, end)):
                    return urls
    raise ValueError("Cannot find a LOSC dataset for %s covering [%d, %d)"
                     % (detector, start, end))


def get_event_urls(detector, event, format='hdf5', duration=32,
                   sample_rate=4096, host=LOSC_URL):
    """Find the URLs of LIGO data files regarding a GW event

    Parameters
    ----------
    detector : `str`
        the prefix of the relevant GW detector

    event : `str`
        the name of the GW event to find

    sample_rate : `int`, optional, default : ``4096``
        the sampling rate (Hz) of files you want to find

    format : `str`, optional, default: ``'hdf5'``
        the file format (extension) you want to find

    duration : `int`, optional, default: ``4096``
        the duration of files you want to find

    host : `str`, optional
        the URL of the remote LOSC server

    Returns
    -------
    urls : `list` of `str`
        the list of remote file URLs that contain data matching the
        relevant parameters
    """
    url = '%s/archive/%s/json/' % (host, event)
    jsonmetadata = read_json(url)
    return parse_file_urls(
        jsonmetadata['strain'], detector, sample_rate=sample_rate,
        format=format, duration=duration)
