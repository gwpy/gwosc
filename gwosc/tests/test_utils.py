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

"""Tests for :mod:`gwosc.utils`
"""

import pytest

from .. import utils

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'


def test_url_segment():
    url = 'X-TEST-123-456.ext'
    assert utils.url_segment(url) == (123, 579)


@pytest.mark.parametrize('url, segment, result', [
    ('A-B-10-1.ext', (0, 10), False),
    ('A-B-10-1.ext', (5, 11), True),
    ('A-B-10-1.ext', (10, 15), True),
    ('A-B-10-1.ext', (11, 15), False),
])
def test_url_overlaps_segment(url, segment, result):
    assert utils.url_overlaps_segment(url, segment) is result


@pytest.mark.parametrize('segment, result', [
    ((1126257414, 1126257414+4096), True),
    ((1126257413, 1126257414+4096), False),
    ((1126257414, 1126257414+4097), False),
])
def test_full_coverage(gw150914_urls, segment, result):
    urls = [u['url'] for u in gw150914_urls]
    assert utils.full_coverage(urls, segment) is result


@pytest.mark.parametrize('seg1, seg2, result', [
    ((10, 11), (0, 10), False),
    ((10, 11), (5, 11), True),
    ((10, 11), (10, 15), True),
    ((10, 11), (11, 15), False),
])
def test_segments_overlap(seg1, seg2, result):
    assert utils.segments_overlap(seg1, seg2) is result
