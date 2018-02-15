# -*- coding: utf-8 -*-
# Copyright Duncan Macleod 2018
#
# This file is part of LOSC-Python.
#
# LOSC-Python is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LOSC-Python is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LOSC-Python.  If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for python-losc

These tests can be executed using `python setup.py test`
"""

import os.path

import pytest

from losc import (
    api as losc_api,
    urls as losc_urls,
)


def check_json_url_list(urllist, keys={'detector', 'format', 'url'}):
    assert isinstance(urllist, list)
    for urld in urllist:
        for key in keys:
            assert key in urld


@pytest.fixture
def gw150914_urls(scope='module'):
    return losc_api.fetch_event_json('GW150914')['strain']


@pytest.fixture
def gw170817_urls(scope='module'):
    return losc_api.fetch_event_json('GW170817')['strain']


# -- losc.api -----------------------------------------------------------------

def test_api_fetch_json():
    url = 'https://losc.ligo.org/archive/1126257414/1126261510/json/'
    out = losc_api.fetch_json(url)
    assert isinstance(out, dict)
    assert len(out['events']) == 1
    assert sorted(out['events']['GW150914']['detectors']) == ['H1', 'L1']
    assert set(out['runs'].keys()) == {'tenyear', 'O1'}

    # check errors (use legit URL that isn't JSON)
    url2 = os.path.dirname(os.path.dirname(url))
    with pytest.raises(ValueError) as exc:
        losc_api.fetch_json(url2)
    assert str(exc.value).startswith(
        "Failed to parse LOSC JSON from {!r}: ".format(url2))


def test_api_fetch_dataset_json():
    start = 934000000
    end = 934100000
    out = losc_api.fetch_dataset_json(start, end)
    assert not out['events']
    assert set(out['runs'].keys()) == {'tenyear', 'S6'}


def test_api_fetch_event_json():
    event = 'GW150914'
    out = losc_api.fetch_event_json(event)
    assert int(out['GPS']) == 1126259462
    assert out['dataset'] == event
    check_json_url_list(out['strain'])


def test_api_fetch_run_json():
    run = 'S6'
    detector = 'L1'
    start = 934000000
    end = 934100000
    out = losc_api.fetch_run_json(run, detector, start, end)
    assert out['dataset'] == run
    assert out['GPSstart'] == start
    assert out['GPSend'] == end
    check_json_url_list(out['strain'])


# -- losc.urls ----------------------------------------------------------------

def test_urls_sieve(gw150914_urls):
    nfiles = len(gw150914_urls)
    sieved = list(losc_urls.sieve(gw150914_urls, detector='L1'))
    assert len(sieved) == nfiles // 2
    sieved = list(losc_urls.sieve(gw150914_urls, detector='L1',
                                  sample_rate=4096))
    assert len(sieved) == nfiles // 4

    with pytest.raises(KeyError):
        list(losc_urls.sieve(gw150914_urls, blah=None))


def test_urls_match(gw150914_urls, gw170817_urls):
    urls = [u['url'] for u in gw150914_urls]
    nfiles = len(urls)
    matched = losc_urls.match(urls, version=1)
    assert len(matched) == nfiles // 2
    for url in matched:
        assert '_V1-' in url

    # test GW170817 for multiple tags
    urls = [u['url'] for u in gw170817_urls]
    with pytest.raises(ValueError) as exc:
        losc_urls.match(urls)
    assert str(exc.value).startswith('multiple LOSC URL tags')

    matched = losc_urls.match(urls, tag='CLN')
    for url in matched:
        assert '_CLN_' in url

    assert losc_urls.match(urls, tag='BLAH') == []
