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

"""Locate files within a given interval on losc.ligo.org
"""

from . import (api, urls as lurls, utils)

__all__ = ['get_urls', 'get_event_urls']
__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'


def get_urls(detector, start, end, host=api.DEFAULT_URL,
             tag=None, version=None, sample_rate=4096, format='hdf5'):
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

    metadata = api.fetch_dataset_json(start, end, host=host)

    # find dataset that provides required data
    for dstype in sorted(metadata, key=lambda x: 0 if x == 'events' else 1):

        # work out how to get the event URLS
        if dstype == 'events':
            def _get_urls(dataset):
                return api.fetch_event_json(dataset, host=host)['strain']
        elif dstype == 'runs':
            def _get_urls(dataset):
                return api.fetch_run_json(dataset, detector, start, end,
                                          host=host)['strain']
        else:
            raise ValueError(
                "Unrecognised LOSC dataset type {!r}".format(dstype))

        for dataset in metadata[dstype]:
            dsmeta = metadata[dstype][dataset]

            # validate IFO is present
            if detector not in dsmeta['detectors']:
                continue

            # get URL list for this dataset
            urls = _get_urls(dataset)

            # match URLs to request
            urls = lurls.match(
                [u['url'] for u in lurls.sieve(
                    urls, detector=detector,
                    sampling_rate=sample_rate, format=format)],
                start, end, tag=tag, version=version)

            # if full span covered, return now
            if utils.full_coverage(urls, (start, end)):
                return urls

    raise ValueError("Cannot find a LOSC dataset for %s covering [%d, %d)"
                     % (detector, start, end))


def get_event_urls(event, format='hdf5', sample_rate=4096, **match):
    meta = api.fetch_event_json(event, host=match.pop('host', api.DEFAULT_URL))
    sieve_kw = {k: match.pop(k) for k in list(match.keys()) if
                k not in {'start', 'end', 'tag', 'version'}}
    return lurls.match(
        [u['url'] for u in lurls.sieve(meta['strain'], format=format,
                                       sample_rate=sample_rate, **sieve_kw)],
        **match)
