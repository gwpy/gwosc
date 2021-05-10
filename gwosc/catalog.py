# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2018-2021)
# SPDX-License-Identifier: MIT

"""Catalog-parsing functions
"""

import warnings

from . import (api, utils)

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'

warnings.warn(
    "the gwosc.catalog module is deprecated and will be removed in "
    "a future release",
    DeprecationWarning,
)

CACHE = {}


def clear_cache():
    global CACHE
    CACHE = {}


def download(catalog, host=api.DEFAULT_URL):
    try:
        return CACHE[catalog]
    except KeyError:
        return CACHE.setdefault(
            catalog,
            api.fetch_legacy_catalog_json(catalog, host=host),
        )


def _nested_values(data):
    if isinstance(data, dict):
        for key in data:
            for item in _nested_values(data[key]):
                yield item
    else:
        yield data


def datasets(catalog, detector=None, segment=None, host=api.DEFAULT_URL):
    data = download(catalog, host=host)["data"]
    datasets = []
    for event, edata in data.items():
        files = edata["files"]
        revision = files["DataRevisionNum"]
        detectors = set(files["OperatingIFOs"].split())
        if detector not in detectors | {None}:
            continue
        urls = [
            url for det in detectors for
            url in _nested_values(files[det])
        ]
        if segment and not (
                urls
                and utils.segments_overlap(segment, utils.urllist_extent(urls))
        ):
            continue
        datasets.append("{0}_{1}".format(event, revision))
    return datasets


def events(catalog, detector=None, segment=None, host=api.DEFAULT_URL):
    return [e.rsplit("_", 1)[0] for e in datasets(
        catalog,
        detector=detector,
        segment=segment,
        host=host,
    )]
