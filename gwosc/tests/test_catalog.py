# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2018-2021)
# SPDX-License-Identifier: MIT

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
