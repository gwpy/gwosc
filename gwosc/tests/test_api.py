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

"""Tests for :mod:`gwosc.api`
"""

import os.path
from io import BytesIO

try:
    from unittest import mock
except ImportError:  # python < 3
    import mock

import pytest

from .. import api

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'


def losc_url(path):
    return '{0}/{1}'.format(api.DEFAULT_URL, path)


def check_json_url_list(urllist, keys={'detector', 'format', 'url'}):
    assert isinstance(urllist, list)
    for urld in urllist:
        for key in keys:
            assert key in urld


@pytest.mark.remote
def test_fetch_json():
    url = 'https://losc.ligo.org/archive/1126257414/1126261510/json/'
    out = api.fetch_json(url)
    assert isinstance(out, dict)
    assert len(out['events']) == 1
    assert sorted(out['events']['GW150914']['detectors']) == ['H1', 'L1']
    assert set(out['runs'].keys()) == {'tenyear', 'O1', 'O1_16KHZ'}

    # check errors (use legit URL that isn't JSON)
    url2 = os.path.dirname(os.path.dirname(url))
    with pytest.raises(ValueError) as exc:
        api.fetch_json(url2)
    assert str(exc.value).startswith(
        "Failed to parse LOSC JSON from {!r}: ".format(url2))


@pytest.mark.local
@mock.patch('gwosc.api.urlopen', return_value=BytesIO(b'{"key": "value"}'))
def test_fetch_json_local(_):
    url = 'anything'
    out = api.fetch_json(url)
    assert isinstance(out, dict)
    assert out['key'] == 'value'


@pytest.mark.remote
def test_fetch_dataset_json():
    start = 934000000
    end = 934100000
    out = api.fetch_dataset_json(start, end)
    assert not out['events']
    assert set(out['runs'].keys()) == {'tenyear', 'S6'}


@pytest.mark.local
@mock.patch('gwosc.api.fetch_json')
def test_fetch_dataset_json_local(fetch):
    start = 934000000
    end = 934100000
    api.fetch_dataset_json(start, end)
    fetch.assert_called_with(
        losc_url('archive/{0}/{1}/json/'.format(start, end)))


@pytest.mark.remote
def test_fetch_event_json():
    event = 'GW150914'
    out = api.fetch_event_json(event)
    assert int(out['GPS']) == 1126259462
    assert out['dataset'] == event
    check_json_url_list(out['strain'])


@pytest.mark.local
@mock.patch('gwosc.api.fetch_json')
def test_fetch_event_json_local(fetch):
    api.fetch_event_json('GW150914')
    fetch.assert_called_with(losc_url('archive/GW150914/json/'))


@pytest.mark.remote
def test_fetch_run_json():
    run = 'S6'
    detector = 'L1'
    start = 934000000
    end = 934100000
    out = api.fetch_run_json(run, detector, start, end)
    assert out['dataset'] == run
    assert out['GPSstart'] == start
    assert out['GPSend'] == end
    check_json_url_list(out['strain'])


@pytest.mark.local
@mock.patch('gwosc.api.fetch_json')
def test_fetch_run_json_local(fetch):
    api.fetch_run_json('S6', 'L1', 934000000, 934100000)
    fetch.assert_called_with(
        losc_url('archive/links/S6/L1/934000000/934100000/json/'))
