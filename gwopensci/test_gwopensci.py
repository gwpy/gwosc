# -*- coding: utf-8 -*-
# Copyright Duncan Macleod 2018
#
# This file is part of GWOpenSci.
#
# GWOpenSci is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GWOpenSci is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GWOpenSci.  If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for gwopensci

These tests can be executed using `python setup.py test`
"""

import os.path
import re

import pytest

from gwopensci import (
    api as gwopensci_api,
    datasets as gwopensci_datasets,
    locate as gwopensci_locate,
    timeline as gwopensci_timeline,
    urls as gwopensci_urls,
    utils as gwopensci_utils,
)


def check_json_url_list(urllist, keys={'detector', 'format', 'url'}):
    assert isinstance(urllist, list)
    for urld in urllist:
        for key in keys:
            assert key in urld


@pytest.fixture
def gw150914_urls(scope='module'):
    return gwopensci_api.fetch_event_json('GW150914')['strain']


@pytest.fixture
def gw170817_urls(scope='module'):
    return gwopensci_api.fetch_event_json('GW170817')['strain']


# -- gwopensci.api-------------------------------------------------------------

def test_api_fetch_json():
    url = 'https://losc.ligo.org/archive/1126257414/1126261510/json/'
    out = gwopensci_api.fetch_json(url)
    assert isinstance(out, dict)
    assert len(out['events']) == 1
    assert sorted(out['events']['GW150914']['detectors']) == ['H1', 'L1']
    assert set(out['runs'].keys()) == {'tenyear', 'O1'}

    # check errors (use legit URL that isn't JSON)
    url2 = os.path.dirname(os.path.dirname(url))
    with pytest.raises(ValueError) as exc:
        gwopensci_api.fetch_json(url2)
    assert str(exc.value).startswith(
        "Failed to parse LOSC JSON from {!r}: ".format(url2))


def test_api_fetch_dataset_json():
    start = 934000000
    end = 934100000
    out = gwopensci_api.fetch_dataset_json(start, end)
    assert not out['events']
    assert set(out['runs'].keys()) == {'tenyear', 'S6'}


def test_api_fetch_event_json():
    event = 'GW150914'
    out = gwopensci_api.fetch_event_json(event)
    assert int(out['GPS']) == 1126259462
    assert out['dataset'] == event
    check_json_url_list(out['strain'])


def test_api_fetch_run_json():
    run = 'S6'
    detector = 'L1'
    start = 934000000
    end = 934100000
    out = gwopensci_api.fetch_run_json(run, detector, start, end)
    assert out['dataset'] == run
    assert out['GPSstart'] == start
    assert out['GPSend'] == end
    check_json_url_list(out['strain'])


# -- gwopensci.datasets -------------------------------------------------------


def test_find_datasets():
    sets = gwopensci_datasets.find_datasets()
    for dset in ('S6', 'O1', 'GW150914', 'GW170817'):
        assert dset in sets
    assert 'tenyear' not in sets

    v1sets = gwopensci_datasets.find_datasets('V1')
    assert 'GW170817' in v1sets
    assert 'GW150914' not in v1sets

    assert gwopensci_datasets.find_datasets('X1') == []

    runsets = gwopensci_datasets.find_datasets(type='run')
    assert 'O1' in runsets
    run_regex = re.compile('\A[OS]\d+\Z')
    for dset in runsets:
        assert run_regex.match(dset)

    with pytest.raises(ValueError):
        gwopensci_datasets.find_datasets(type='badtype')


def test_event_gps():
    assert gwopensci_datasets.event_gps('GW170817') == 1187008882.43
    with pytest.raises(ValueError) as exc:
        gwopensci_datasets.event_gps('GW123456')
    assert str(exc.value) == 'no event dataset found for \'GW123456\''


def test_event_at_gps():
    assert gwopensci_datasets.event_at_gps(1187008882) == 'GW170817'
    with pytest.raises(ValueError) as exc:
        gwopensci_datasets.event_at_gps(1187008882, tol=.1)
    assert str(exc.value) == 'no event found within 0.1 seconds of 1187008882'


def test_run_segment():
    assert gwopensci_datasets.run_segment('O1') == (1126051217, 1137254417)
    with pytest.raises(ValueError) as exc:
        gwopensci_datasets.run_segment('S7')
    assert str(exc.value) == 'no run dataset found for \'S7\''


def test_run_at_gps():
    assert gwopensci_datasets.run_at_gps(1135136350) == 'O1'
    with pytest.raises(ValueError) as exc:
        gwopensci_datasets.run_at_gps(0)
    assert str(exc.value) == 'no run dataset found containing GPS 0'


# -- gwopensci.locate ---------------------------------------------------------

def test_get_urls():
    # test simple fetch for S6 data returns only files within segment
    detector = 'L1'
    start = 934000000
    end = 934100000
    span = (start, end)
    urls = gwopensci_locate.get_urls(detector, start, end)
    for url in urls:
        assert os.path.basename(url).startswith(
            '{}-{}'.format(detector[0], detector))
        assert gwopensci_utils.segments_overlap(
            gwopensci_utils.url_segment(url), span)


def test_get_event_urls(gw150914_urls):
    # find latest version by brute force
    latestv = sorted(
        gwopensci_urls.URL_REGEX.match(
            os.path.basename(u['url'])).groupdict()['version'] for
        u in gw150914_urls)[-1]

    event = 'GW150914'
    urls = gwopensci_locate.get_event_urls(event)
    for url in urls:
        assert url.endswith('.hdf5')  # default format
        assert '_4_' in url  # default sample rate
        assert '_{}-'.format(latestv) in url  # highest matched version

    urls = gwopensci_locate.get_event_urls(event, version=1)
    for url in urls:
        assert '_V1-' in url


# -- gwopensci.timeline -------------------------------------------------------

@pytest.mark.parametrize('flag, start, end, result', [
    ('H1_DATA', 1126051217, 1126151217, [
        (1126073529, 1126114861),
        (1126121462, 1126123267),
        (1126123553, 1126126832),
        (1126139205, 1126139266),
        (1126149058, 1126151217),
    ]),
    ('L1_DATA', 1126259446, 1126259478, [
        (1126259446, 1126259478),
    ])
])
def test_timeline_get_segments(flag, start, end, result):
    assert gwopensci_timeline.get_segments(flag, start, end) == result


# -- gwopensci.urls -----------------------------------------------------------

def test_urls_sieve(gw150914_urls):
    nfiles = len(gw150914_urls)
    sieved = list(gwopensci_urls.sieve(gw150914_urls, detector='L1'))
    assert len(sieved) == nfiles // 2
    sieved = list(gwopensci_urls.sieve(gw150914_urls, detector='L1',
                                       sample_rate=4096))
    assert len(sieved) == nfiles // 4

    with pytest.raises(KeyError):
        list(gwopensci_urls.sieve(gw150914_urls, blah=None))


def test_urls_match(gw150914_urls, gw170817_urls):
    urls = [u['url'] for u in gw150914_urls]
    nfiles = len(urls)
    matched = gwopensci_urls.match(urls, version=1)
    assert len(matched) == nfiles // 2
    for url in matched:
        assert '_V1-' in url

    # test GW170817 for multiple tags
    urls = [u['url'] for u in gw170817_urls]
    with pytest.raises(ValueError) as exc:
        gwopensci_urls.match(urls)
    assert str(exc.value).startswith('multiple LOSC URL tags')

    matched = gwopensci_urls.match(urls, tag='CLN')
    for url in matched:
        assert '_CLN_' in url

    assert gwopensci_urls.match(urls, tag='BLAH') == []


# -- gwopensci ----------------------------------------------------------------

def test_url_segment():
    url = 'X-TEST-123-456.ext'
    assert gwopensci_utils.url_segment(url) == (123, 579)


@pytest.mark.parametrize('url, segment, result', [
    ('A-B-10-1.ext', (0, 10), False),
    ('A-B-10-1.ext', (5, 11), True),
    ('A-B-10-1.ext', (10, 15), True),
    ('A-B-10-1.ext', (11, 15), False),
])
def test_url_overlaps_segment(url, segment, result):
    assert gwopensci_utils.url_overlaps_segment(url, segment) is result


@pytest.mark.parametrize('segment, result', [
    ((1126257414, 1126257414+4096), True),
    ((1126257413, 1126257414+4096), False),
    ((1126257414, 1126257414+4097), False),
])
def test_full_coverage(gw150914_urls, segment, result):
    urls = [u['url'] for u in gw150914_urls]
    assert gwopensci_utils.full_coverage(urls, segment) is result


@pytest.mark.parametrize('seg1, seg2, result', [
    ((10, 11), (0, 10), False),
    ((10, 11), (5, 11), True),
    ((10, 11), (10, 15), True),
    ((10, 11), (11, 15), False),
])
def test_segments_overlap(seg1, seg2, result):
    assert gwopensci_utils.segments_overlap(seg1, seg2) is result
