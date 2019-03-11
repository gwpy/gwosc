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

import warnings

from . import (
    api,
    datasets,
    urls as lurls,
    utils,
)

__all__ = ['get_urls', 'get_event_urls']
__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'


def get_urls(
        detector, start, end,
        dataset=None,
        tag=None,
        version=None,
        sample_rate=4096,
        format='hdf5',
        host=api.DEFAULT_URL,
):
    """Fetch the metadata from LOSC regarding a given GPS interval

    Parameters
    ----------
    detector : `str`
        the prefix of the relevant GW detector

    start : `int`
        the GPS start time of your query

    end : `int`
        the GPS end time of your query

    dataset : `str`, `None`, optional
        the name of the dataset to query, e.g. ``'GW150914'``

    version : `int`, `None`, optional
        the data-release version for the selected datasets

    sample_rate : `int`, optional, default : ``4096``
        the sampling rate (Hz) of files you want to find

    format : `str`, optional, default: ``'hdf5'``
        the file format (extension) you want to find

    host : `str`, optional
        the URL of the remote LOSC server

    Returns
    -------
    urls : `list` of `str`
        the list of remote file URLs that contain data matching the
        relevant parameters
    """
    start = int(start)
    end = int(end)

    if tag is not None:
        warnings.warn(
            "the `tag` keyword to get_urls is deprecated, GWOSC no longer "
            "releases multiple datasets for events, please use the `dataset` "
            "and `version` keyword arguments to manually select the host "
            "dataset for URLs",
            DeprecationWarning,
        )

    dataset_metadata = [
        ("event",
         lambda x: api.fetch_catalog_event_json(x, host=host),
         ),
        ("run",
         lambda x: api.fetch_run_json(x, detector, start, end, host=host),
         ),
    ]

    if dataset:
        dstype = datasets.dataset_type(dataset)
        dataset_metadata = [(dstype, dict(dataset_metadata)[dstype])]

    for dstype, _get_urls in dataset_metadata:
        if dataset:
            dsets = [dataset]
        else:
            dsets = datasets.find_datasets(
                type=dstype,
                detector=detector,
                segment=(start, end),
                host=host,
            )
        for dst in dsets:
            # get URL list for this dataset
            urls = _get_urls(dst)["strain"]

            # match URLs to request
            urls = lurls.match(
                [u['url'] for u in lurls.sieve(
                    urls, detector=detector,
                    sampling_rate=sample_rate, format=format)],
                start, end, version=version)

            # if full span covered, return now
            if utils.full_coverage(urls, (start, end)):
                return urls

    raise ValueError("Cannot find a LOSC dataset for %s covering [%d, %d)"
                     % (detector, start, end))


def get_event_urls(event, format='hdf5', sample_rate=4096, **match):
    meta = api.fetch_catalog_event_json(
        event,
        host=match.pop('host', api.DEFAULT_URL),
    )
    sieve_kw = {k: match.pop(k) for k in list(match.keys()) if
                k not in {'start', 'end', 'tag', 'version'}}
    return lurls.match(
        [u['url'] for u in lurls.sieve(meta['strain'], format=format,
                                       sample_rate=sample_rate, **sieve_kw)],
        **match)
