# -*- coding: utf-8 -*-
# Copyright Duncan Macleod 2018
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

"""Tests for :mod:`gwosc.urls`
"""

import pytest

from .. import urls as gwosc_urls

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'


@pytest.mark.remote
def test_sieve(gw150914_urls):
    nfiles = len(gw150914_urls)
    sieved = list(gwosc_urls.sieve(gw150914_urls, detector='L1'))
    assert len(sieved) == nfiles // 2
    sieved = list(gwosc_urls.sieve(gw150914_urls, detector='L1',
                                   sample_rate=4096))
    assert len(sieved) == nfiles // 4

    with pytest.raises(KeyError):
        list(gwosc_urls.sieve(gw150914_urls, blah=None))


@pytest.mark.remote
def test_match(gw150914_urls, gw170817_urls):
    urls = [u['url'] for u in gw150914_urls]
    nfiles = len(urls)
    matched = gwosc_urls.match(urls, start=1126259500)  # after 32s files end
    assert len(matched) == nfiles // 2
    for url in matched:
        assert '_R1-' in url


def test_match_tags():
    urls = [
        "/path/to/X-X1_LOSC_C00_4KHZ_R1-0-10.gwf",
        "/path/to/X-X1_LOSC_C01_4KHZ_R1-0-10.gwf",
    ]
    with pytest.raises(ValueError) as exc:
        gwosc_urls.match(urls)
    assert str(exc.value).startswith('multiple LOSC URL tags')

    matched = gwosc_urls.match(urls, tag='C01')
    assert matched == [urls[1]]

    assert not gwosc_urls.match(urls, tag='BLAH')
    assert not gwosc_urls.match(urls, start=1e12)
    assert not gwosc_urls.match(urls, end=0)


# -- local tests


URLS = [
    {'url': 'X-X1_LOSC_TEST_4_V1-0-1.ext',
     'detector': 'X1',
     'sampling_rate': 100},
    {'url': 'Y-Y1_LOSC_TEST_16_V2-1-1.ext',
     'detector': 'Y1',
     'sampling_rate': 200},
    {'url': 'Y-Y1_LOSC_TEST2_16_V2-1-1.ext',
     'detector': 'Y1',
     'sampling_rate': 200},
]


def test_sieve_local():
    assert list(gwosc_urls.sieve(URLS, detector='X1')) == URLS[:1]
    assert list(gwosc_urls.sieve(URLS, sample_rate=200)) == URLS[1:]


def test_match_local():
    urls = [u['url'] for u in URLS]
    with pytest.raises(ValueError) as exc:
        gwosc_urls.match(urls)
    assert str(exc.value).startswith('multiple LOSC URL tags')
    assert gwosc_urls.match(urls, tag="TEST", start=0, end=1) == [urls[0]]
    assert gwosc_urls.match(urls, tag="TEST", version=2) == [urls[1]]
    assert gwosc_urls.match(urls, tag="TEST2", version="R2") == [urls[2]]
