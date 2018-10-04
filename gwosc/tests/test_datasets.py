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

"""Tests for :mod:`gwosc.datasets`
"""

import re
try:
    from unittest import mock
except ImportError:  # python < 3
    import mock

import pytest

from .. import datasets

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'


DATASET_JSON = {
    'events': {
        'GW150914': {'GPStime': 12345, 'detectors': ['H1', 'L1']},
        'GW151226': {'GPStime': 12347, 'detectors': ['H1', 'L1']},
    },
    'runs': {
        'S1': {'GPSstart': 0, 'GPSend': 1, 'detectors': ['H1', 'L1', 'V1']},
        'tenyear': None,
    },
}


@pytest.mark.remote
def test_find_datasets():
    sets = datasets.find_datasets()
    for dset in ('S6', 'O1', 'GW150914', 'GW170817'):
        assert dset in sets
    assert 'tenyear' not in sets

    v1sets = datasets.find_datasets('V1')
    assert 'GW170817' in v1sets
    assert 'GW150914' not in v1sets

    assert datasets.find_datasets('X1') == []

    runsets = datasets.find_datasets(type='run')
    assert 'O1' in runsets
    run_regex = re.compile('\A[OS]\d+(_16KHZ)?\Z')
    for dset in runsets:
        assert run_regex.match(dset)

    with pytest.raises(ValueError):
        datasets.find_datasets(type='badtype')


@pytest.mark.local
@mock.patch('gwosc.api.fetch_dataset_json', return_value=DATASET_JSON)
def test_find_datasets_local(fetch):
    sets = datasets.find_datasets()
    assert datasets.find_datasets() == ['GW150914', 'GW151226', 'S1']
    assert datasets.find_datasets(detector='V1') == ['S1']
    assert datasets.find_datasets(type='event') == ['GW150914', 'GW151226']
    assert datasets.find_datasets(type='event', detector='V1') == []


@pytest.mark.remote
def test_event_gps():
    assert datasets.event_gps('GW170817') == 1187008882.43
    with pytest.raises(ValueError) as exc:
        datasets.event_gps('GW123456')
    assert str(exc.value) == 'no event dataset found for \'GW123456\''


@pytest.mark.local
@mock.patch('gwosc.api.fetch_event_json', return_value={
    'GPS': 12345,
    'something else': None,
})
def test_event_gps_local(fetch):
    assert datasets.event_gps('GW150914') == 12345
    fetch.side_effect = ValueError('test')
    with pytest.raises(ValueError) as exc:
        datasets.event_gps('something')
    assert str(exc.value) == 'no event dataset found for \'something\''


@pytest.mark.remote
def test_event_at_gps():
    assert datasets.event_at_gps(1187008882) == 'GW170817'
    with pytest.raises(ValueError) as exc:
        datasets.event_at_gps(1187008882, tol=.1)
    assert str(exc.value) == 'no event found within 0.1 seconds of 1187008882'


@pytest.mark.local
@mock.patch('gwosc.api.fetch_dataset_json', return_value=DATASET_JSON)
def test_event_at_gps_local(fetch):
    assert datasets.event_at_gps(12345) == 'GW150914'
    with pytest.raises(ValueError):
        datasets.event_at_gps(12349)


@pytest.mark.remote
def test_run_segment():
    assert datasets.run_segment('O1') == (1126051217, 1137254417)
    with pytest.raises(ValueError) as exc:
        datasets.run_segment('S7')
    assert str(exc.value) == 'no run dataset found for \'S7\''


@pytest.mark.local
@mock.patch('gwosc.api.fetch_dataset_json', return_value=DATASET_JSON)
def test_run_segment_local(fetch):
    assert datasets.run_segment('S1') == (0, 1)
    with pytest.raises(ValueError) as exc:
        datasets.run_segment('S2')


@pytest.mark.remote
def test_run_at_gps():
    assert datasets.run_at_gps(1135136350) in {'O1', 'O1_16KHZ'}
    with pytest.raises(ValueError) as exc:
        datasets.run_at_gps(0)
    assert str(exc.value) == 'no run dataset found containing GPS 0'


@pytest.mark.local
@mock.patch('gwosc.api.fetch_dataset_json', return_value=DATASET_JSON)
def test_run_at_gps_local(fetch):
    assert datasets.run_at_gps(0) == 'S1'
    with pytest.raises(ValueError):
        datasets.run_at_gps(10)
