# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2018-2021)
# SPDX-License-Identifier: MIT

"""
`gwosc.locate` provides functions to determine the file URLs containing
data for a specific dataset.

You can search for remote data URLS based on the event name:

>>> from gwosc.locate import get_event_urls
>>> get_event_urls('GW150914')
['https://www.gw-openscience.org/eventapi/json/GWTC-1-confident/GW150914/v3/H-H1_GWOSC_4KHZ_R1-1126259447-32.hdf5',
 'https://www.gw-openscience.org/eventapi/json/GWTC-1-confident/GW150914/v3/H-H1_GWOSC_4KHZ_R1-1126257415-4096.hdf5',
 'https://www.gw-openscience.org/eventapi/json/GWTC-1-confident/GW150914/v3/L-L1_GWOSC_4KHZ_R1-1126259447-32.hdf5',
 'https://www.gw-openscience.org/eventapi/json/GWTC-1-confident/GW150914/v3/L-L1_GWOSC_4KHZ_R1-1126257415-4096.hdf5']

You can down-select the URLs using keyword arguments:

>>> get_event_urls('GW150914', detector='L1', duration=32)
['https://www.gw-openscience.org/eventapi/json/GWTC-1-confident/GW150914/v3/L-L1_GWOSC_4KHZ_R1-1126259447-32.hdf5']

You can search for remote data URLs based on the GPS time interval as
follows:

>>> from gwosc.locate import get_urls
>>> get_urls('L1', 968650000, 968660000)
['https://www.gw-openscience.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968646656-4096.hdf5',
 'https://www.gw-openscience.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968650752-4096.hdf5',
 'https://www.gw-openscience.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968654848-4096.hdf5',
 'https://www.gw-openscience.org/archive/data/S6/967835648/L-L1_LOSC_4_V1-968658944-4096.hdf5']

By default, this method will return the paths to HDF5 files for the 4 kHz
sample-rate data, these can be specified as keyword arguments.
For full information, see :func:`get_urls`.
"""  # noqa: E501

import warnings

from . import (
    api,
    datasets,
    urls as lurls,
    utils,
)

__all__ = ['get_urls', 'get_run_urls', 'get_event_urls']
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
    """Fetch the URLs from GWOSC regarding a given GPS interval

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
        the URL of the remote GWOSC server

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

    for dstype in ("event", "run"):
        dsets = datasets._iter_datasets(
            match=dataset,
            type=dstype,
            detector=detector,
            segment=(start, end),
            version=version,
            host=host,
        )

        for dst in dsets:
            # get URL list for this dataset
            if dstype == "run":
                urls = get_run_urls(
                    dst,
                    detector,
                    start,
                    end,
                    host=host,
                    sample_rate=sample_rate,
                    format=format,
                )
            else:
                urls = get_event_urls(
                    dst,
                    detector=detector,
                    start=start,
                    end=end,
                    format=format,
                    sample_rate=sample_rate,
                    version=version,
                )

            # if full span covered, return now
            if utils.full_coverage(urls, (start, end)):
                return urls

    raise ValueError("Cannot find a GWOSC dataset for %s covering [%d, %d)"
                     % (detector, start, end))


def get_run_urls(
        run,
        detector,
        start,
        end,
        format='hdf5',
        sample_rate=4096,
        **match
):
    """Fetch the URLs from GWOSC regarding a given event

    Parameters
    ----------
    event : `str`
        the ID of the event

    detector : `str`, optional
        the detector for files you want to find

    start : `int`
        the GPS start time of your query

    end : `int`
        the GPS end time of your query

    format : `str`, optional, default: ``'hdf5'``
        the file format (extension) you want to find

    sample_rate : `int`, optional, default : ``4096``
        the sampling rate (Hz) of files you want to find

    host : `str`, optional
        the URL of the remote GWOSC server

    version : `int`, `None`, optional
        the data-release version for the selected datasets

    Returns
    -------
    urls : `list` of `str`
        the list of remote file URLs that contain data matching the
        relevant parameters
    """
    # get the URL file list for this run segment
    meta = api.fetch_run_json(
        run,
        detector,
        gpsstart=start,
        gpsend=end,
        host=match.pop('host', api.DEFAULT_URL),
    )

    # filter
    return _urls(lurls.sieve(
        meta["strain"],
        format=format,
        sampling_rate=sample_rate,
        **match
    ))


def get_event_urls(
        event,
        catalog=None,
        version=None,
        detector=None,
        start=None,
        end=None,
        format='hdf5',
        sample_rate=4096,
        host=api.DEFAULT_URL,
        **match
):
    """Fetch the URLs from GWOSC regarding a given event

    Parameters
    ----------
    event : `str`
        the ID of the event

    detector : `str`, optional
        the detector for files you want to find

    format : `str`, optional, default: ``'hdf5'``
        the file format (extension) you want to find

    sample_rate : `int`, optional, default : ``4096``
        the sampling rate (Hz) of files you want to find

    host : `str`, optional
        the URL of the remote GWOSC server

    start : `int`
        the GPS start time of your query

    end : `int`
        the GPS end time of your query

    version : `int`, `None`, optional
        the data-release version for the selected datasets

    Returns
    -------
    urls : `list` of `str`
        the list of remote file URLs that contain data matching the
        relevant parameters
    """
    # get the URL file list for this event
    meta = list(api._fetch_allevents_event_json(
        event,
        catalog=catalog,
        version=version,
        full=True,
        host=host,
    )["events"].values())[0]
    strain = meta["strain"]

    # format start and end as a segment
    if start is None and end is None:
        segment = None
    else:
        segment = (
            -float('inf') if start is None else start,
            +float('inf') if end is None else end,
        )

    # then filter on everything els
    return _urls(lurls.sieve(
        strain,
        detector=detector,
        format=format,
        sampling_rate=sample_rate,
        segment=segment,
        **match
    ))


def _urls(strain):
    return [u["url"] for u in strain]
