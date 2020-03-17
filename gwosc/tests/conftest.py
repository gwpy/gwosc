# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University, 2018-2020
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

"""Helpers for tests
"""

import os

import pytest

from ..api import (
    fetch_event_json,
    fetch_run_json,
)

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'

# unset these variables to allow the tests to run with pybuild
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

try:
    autouseyield = pytest.yield_fixture(autouse=True)
except AttributeError:  # pytest > 3.0.0
    autouseyield = pytest.fixture(autouse=True)


def _event_strain(name, **kwargs):
    return list(
        fetch_event_json(name, **kwargs)["events"].values()
    )[0]["strain"]


@pytest.fixture(scope="module")
def gw150914_strain():
    return _event_strain('GW150914', version=3)


@pytest.fixture(scope="module")
def gw170817_strain():
    return _event_strain('GW170817', version=2)


@pytest.fixture(scope="module")
def o1_strain():
    return fetch_run_json("O1", "L1", 1126257415, 1126261511)["strain"]


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
