# -*- coding: utf-8 -*-
# Copyright Duncan Macleod 2019
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

"""Catalog-parsing functions
"""

import json

from . import (api, utils)

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'

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
            api.fetch_catalog_json(catalog, host=host)
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
        urls = [url for det in detectors for url in _nested_values(files[det])]
        if segment and not (
                urls and
                utils.segments_overlap(segment, utils.urllist_extent(urls))
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
