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


def test_sieve(gw150914_urls):
    nfiles = len(gw150914_urls)
    sieved = list(gwosc_urls.sieve(gw150914_urls, detector='L1'))
    assert len(sieved) == nfiles // 2
    sieved = list(gwosc_urls.sieve(gw150914_urls, detector='L1',
                                   sample_rate=4096))
    assert len(sieved) == nfiles // 4

    with pytest.raises(KeyError):
        list(gwosc_urls.sieve(gw150914_urls, blah=None))


def test_match(gw150914_urls, gw170817_urls):
    urls = [u['url'] for u in gw150914_urls]
    nfiles = len(urls)
    matched = gwosc_urls.match(urls, version=1)
    assert len(matched) == nfiles // 2
    for url in matched:
        assert '_V1-' in url

    # test GW170817 for multiple tags
    urls = [u['url'] for u in gw170817_urls]
    with pytest.raises(ValueError) as exc:
        gwosc_urls.match(urls)
    assert str(exc.value).startswith('multiple LOSC URL tags')

    matched = gwosc_urls.match(urls, tag='CLN')
    for url in matched:
        assert '_CLN_' in url

    assert not gwosc_urls.match(urls, tag='BLAH')
    assert not gwosc_urls.match(urls, start=1e12)
    assert not gwosc_urls.match(urls, end=0)
