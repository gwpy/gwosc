# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2018-2021)
# SPDX-License-Identifier: MIT

"""Tests for :mod:`gwosc.locate`
"""

import os.path
from pathlib import Path

import pytest

from .. import (
    locate,
    utils,
)

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'


@pytest.mark.remote
def test_get_urls():
    # test simple fetch for S6 data returns only files within segment
    detector = 'L1'
    start = 934000000
    end = 934100000
    span = (start, end)
    urls = locate.get_urls(detector, start, end)
    for url in urls:
        assert os.path.basename(url).startswith(
            '{}-{}'.format(detector[0], detector))
        assert utils.segments_overlap(
            utils.url_segment(url), span)

    # test fetch for GW170817 data
    assert len(locate.get_urls(
        'L1', 1187007040, 1187009088,
        dataset="GW170817-v3",
    )) == 2

    # test for O1 data
    assert len(locate.get_urls("L1", 1135136228, 1135140324)) == 2

    # assert no hits raises exception
    with pytest.raises(ValueError):  # no data in 1980
        locate.get_urls(detector, 0, 1)
    with pytest.raises(ValueError):  # no Virgo data for S6
        locate.get_urls('V1', start, end)


@pytest.mark.remote
def test_get_urls_version():
    """Regression test against version not being respected in get_urls
    """
    urls = locate.get_urls('L1', 1187008877, 1187008887, version=2)
    assert Path(urls[0]).name == "L-L1_LOSC_CLN_4_V1-1187007040-2048.hdf5"


@pytest.mark.remote
def test_get_urls_deprecated_tag():
    # test `tag` prints a warning
    pytest.deprecated_call(
        locate.get_urls,
        "L1",
        1187007040,
        1187009088,
        tag="TEST",
    )


@pytest.mark.remote
def test_get_event_urls():
    urls = locate.get_event_urls("GW150914-v3", sample_rate=4096)
    assert len(urls) == 4
    for url in urls:
        assert "_4KHZ" in url


@pytest.mark.remote
def test_get_event_urls_segment():
    urls = locate.get_event_urls(
        "GW150914-v1",
        start=1126257415,
        end=1126257425,
    )
    assert len(urls) == 2
    for url in urls:  # check that these are the 4096-second files
        assert "-4096." in url


@pytest.mark.remote
def test_get_urls_gw170104():
    # check that we can find the right URL from an event dataset for
    # a GPS time that doesn't overlap with the event, and ends before
    # the start of the 32-second files (this used to not work)
    urls = locate.get_urls('L1', 1167558912.6, 1167559012.6)
    assert list(map(os.path.basename, urls)) == [
        "L-L1_GWOSC_4KHZ_R1-1167557889-4096.hdf5",
    ]
