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

"""Tests for :mod:`gwosc.catalog`

This module is deprecated and will be removed soon
"""

import importlib

import pytest

with pytest.deprecated_call():
    catalog = importlib.import_module("gwosc.catalog")

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'


@pytest.mark.remote
def test_download():
    data = catalog.download("GWTC-1-confident")
    assert "GW150914" in data["data"]

    # check that the cache works properly
    data2 = catalog.download("GWTC-1-confident")
    assert data2 is data


@pytest.mark.remote
def test_datasets():
    datasets = catalog.datasets("GWTC-1-confident")
    assert "GW150914_R1" in datasets


@pytest.mark.remote
def test_datasets_detector():
    datasets = catalog.datasets("GWTC-1-confident", detector="V1")
    assert "GW150914_R1" not in datasets
    assert "GW170817_R1" in datasets


@pytest.mark.remote
def test_events():
    assert "GW150914" in catalog.events("GWTC-1-confident")
