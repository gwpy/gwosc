# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2018-2021)
# SPDX-License-Identifier: MIT

"""Tests for :mod:`gwosc.urls`
"""

import pytest

from .. import urls as gwosc_urls

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'


@pytest.mark.remote
def test_sieve(gw150914_strain):
    nfiles = len(gw150914_strain)
    sieved = list(gwosc_urls.sieve(
        gw150914_strain,
        detector='L1',
    ))
    assert len(sieved) == nfiles // 2
    sieved = list(gwosc_urls.sieve(
        gw150914_strain,
        detector='L1',
        sampling_rate=4096,
    ))
    assert len(sieved) == nfiles // 4


# -- local tests

def test_sieve_local(mock_strain):
    assert list(
        gwosc_urls.sieve(mock_strain, detector='X1'),
    ) == mock_strain[:2]
    assert list(
        gwosc_urls.sieve(mock_strain, sampling_rate=16384),
    ) == mock_strain[3:]


def test_sieve_error(mock_strain):
    with pytest.raises(TypeError):
        list(gwosc_urls.sieve(mock_strain, blah=1))


def test_match_local(mock_urls):
    assert gwosc_urls.match(
        mock_urls,
        tag="TEST",
        start=0,
        end=1,
    ) == mock_urls[:1]
    assert gwosc_urls.match(
        mock_urls,
        sample_rate=16384,
    ) == mock_urls[3:]
    assert gwosc_urls.match(
        mock_urls,
        tag="TEST2",
        version="R2",
        sample_rate=16384,
    ) == mock_urls[3:]


def test_match_local_tag_error(mock_urls):
    with pytest.raises(ValueError) as exc:
        gwosc_urls.match(mock_urls)
    assert str(exc.value).startswith('multiple GWOSC URL tags')


def test_match_empty():
    assert gwosc_urls.match([]) == []
