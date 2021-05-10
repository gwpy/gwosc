# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2018-2021)
# SPDX-License-Identifier: MIT

"""Helpers for tests
"""

import os

import pytest

from ..api import (
    fetch_event_json,
)

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'

# unset these variables to allow the tests to run with pybuild
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)


def _event_strain(name, **kwargs):
    return list(
        fetch_event_json(name, **kwargs)["events"].values()
    )[0]["strain"]


@pytest.fixture(scope="module")
def gw150914_strain():
    return _event_strain('GW150914', version=3)


@pytest.fixture
def mock_strain():
    return [
        {'url': 'X-X1_LOSC_TEST_4_V1-0-32.ext',
         'GPSstart': 0,
         'duration': 32,
         'detector': 'X1',
         'sampling_rate': 4096},
        {'url': 'X-X1_LOSC_TEST_4_V1-32-32.ext',
         'GPSstart': 32,
         'duration': 32,
         'detector': 'X1',
         'sampling_rate': 4096},
        {'url': 'Y-Y1_LOSC_TEST2_4_V1-0-32.ext',
         'GPSstart': 0,
         'duration': 32,
         'detector': 'Y1',
         'sampling_rate': 4096},
        {'url': 'Y-Y1_LOSC_TEST2_16_V2-0-32.ext',
         'GPSstart': 0,
         'duration': 32,
         'detector': 'Y1',
         'sampling_rate': 16384},
    ]


@pytest.fixture
def mock_urls(mock_strain):
    return [u["url"] for u in mock_strain]
