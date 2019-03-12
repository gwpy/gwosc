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
CATALOG_JSON = {
    'data': {
        'GW150914': {
            'files': {
                'DataRevisionNum': 'R1',
                'OperatingIFOs': "H1 L1",
                'H1': {},
                'L1': {},
            },
        },
    }
}


@pytest.mark.remote
def test_find_datasets():
    sets = datasets.find_datasets()
    for dset in ('S6', 'O1', 'GW150914', 'GW170817'):
        assert dset in sets
    assert 'tenyear' not in sets
    assert 'history' not in sets


@pytest.mark.remote
def test_find_datasets_detector():
    v1sets = datasets.find_datasets('V1')
    assert 'GW170817' in v1sets
    assert 'GW150914' not in v1sets

    assert datasets.find_datasets('X1', type="run") == []


@pytest.mark.remote
def test_find_datasets_type():
    runsets = datasets.find_datasets(type='run')
    assert 'O1' in runsets
    run_regex = re.compile(r'\A[OS]\d+(_\d+KHZ)?(_[RV]\d+)?\Z')
    for dset in runsets:
        assert run_regex.match(dset)

    assert datasets.find_datasets(type='badtype') == []


@pytest.mark.remote
def test_find_datasets_segment():
    sets = datasets.find_datasets(segment=(1126051217, 1137254417))
    assert "GW150914" in sets
    assert "GW170817" not in sets


@pytest.mark.remote
def test_find_datasets_match():
    assert "O1" not in datasets.find_datasets(match="GW")


@mock.patch('gwosc.api.fetch_dataset_json', return_value=DATASET_JSON)
@mock.patch('gwosc.api.fetch_catalog_json', return_value=CATALOG_JSON)
@mock.patch(
    'gwosc.api.fetch_catalog_event_json',
    return_value={
        "strain": [
            {"url": "https://test.com/X-X1-123-456.gwf",
             "detector": "L1",
             },
            {"url": "https://test.com/X-X1-234-567.gwf",
             "detector": "L1",
             },
        ],
    },
)
@mock.patch("gwosc.datasets.CATALOGS", ["GWTC-1-confident"])
def test_find_datasets_local(fcej, fcj, fdj):
    assert datasets.find_datasets() == [
        "GW150914",
        "GWTC-1-confident",
        'S1',
    ]
    assert datasets.find_datasets(detector='V1') == [
        "GWTC-1-confident",
        "S1",
    ]
    assert datasets.find_datasets(type='event') == ['GW150914']
    assert datasets.find_datasets(type='event', detector='V1') == []


@mock.patch(
    "gwosc.catalog.events",
    side_effect=[ValueError, []],
)
def test_find_datasets_catalog_error(_):
    assert datasets.find_datasets(type="catalog") == ["GWTC-1-marginal"]


@pytest.mark.remote
def test_event_gps():
    assert datasets.event_gps('GW170817') == 1187008882.4
    with pytest.raises(ValueError) as exc:
        datasets.event_gps('GW123456')
    assert str(exc.value) == 'no event dataset found for \'GW123456\''


@mock.patch('gwosc.api.fetch_catalog_event_json', return_value={
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
def test_event_segment():
    assert datasets.event_segment("GW170817") == (1187006835, 1187010931)


@mock.patch('gwosc.api.fetch_catalog_event_json', return_value={
    "strain": [
        {"url": "https://test.com/X-X1-123-456.gwf", "detector": "X1"},
        {"url": "https://test.com/X-X1-234-567.gwf", "detector": "Y1"},
    ],
})
def test_event_segment_local(fetch):
    assert datasets.event_segment("GW170817") == (123, 801)
    assert datasets.event_segment("GW170817", detector="X1") == (123, 579)


@pytest.mark.remote
def test_event_at_gps():
    assert datasets.event_at_gps(1187008882) == 'GW170817'
    with pytest.raises(ValueError) as exc:
        datasets.event_at_gps(1187008882, tol=.1)
    assert str(exc.value) == 'no event found within 0.1 seconds of 1187008882'


@mock.patch('gwosc.api.fetch_dataset_json', return_value=DATASET_JSON)
def test_event_at_gps_local(fetch):
    assert datasets.event_at_gps(12345) == 'GW150914'
    with pytest.raises(ValueError):
        datasets.event_at_gps(12349)


@pytest.mark.remote
def test_event_detectors():
    assert datasets.event_detectors("GW150914") == {"H1", "L1"}
    assert datasets.event_detectors("GW170814") == {"H1", "L1", "V1"}


@mock.patch("gwosc.api.fetch_catalog_event_json", return_value={
    "strain": [{"detector": "A1"}, {"detector": "A1"}, {"detector": "B1"}],
})
def test_event_detectors_local(fcej):
    assert datasets.event_detectors("test") == {"A1", "B1"}


@pytest.mark.remote
def test_run_segment():
    assert datasets.run_segment('O1') == (1126051217, 1137254417)
    with pytest.raises(ValueError) as exc:
        datasets.run_segment('S7')
    assert str(exc.value) == 'no run dataset found for \'S7\''


@mock.patch('gwosc.api.fetch_dataset_json', return_value=DATASET_JSON)
def test_run_segment_local(fetch):
    assert datasets.run_segment('S1') == (0, 1)
    with pytest.raises(ValueError):
        datasets.run_segment('S2')


@pytest.mark.remote
def test_run_at_gps():
    assert datasets.run_at_gps(1135136350) in {'O1', 'O1_16KHZ'}
    with pytest.raises(ValueError) as exc:
        datasets.run_at_gps(0)
    assert str(exc.value) == 'no run dataset found containing GPS 0'


@mock.patch('gwosc.api.fetch_dataset_json', return_value=DATASET_JSON)
def test_run_at_gps_local(fetch):
    assert datasets.run_at_gps(0) == 'S1'
    with pytest.raises(ValueError):
        datasets.run_at_gps(10)


@pytest.mark.remote
def test_dataset_type():
    assert datasets.dataset_type("O1") == "run"
    assert datasets.dataset_type("GW150914") == "event"
    assert datasets.dataset_type("GWTC-1-confident") == "catalog"
    with pytest.raises(ValueError):
        datasets.dataset_type("invalid")


@mock.patch(
    'gwosc.datasets.find_datasets',
    side_effect=[["testrun"], [],  ["testevent"], [], [], []],
)
def test_dataset_type_local(find):
    assert datasets.dataset_type("testevent") == "event"
    with pytest.raises(ValueError):
        datasets.dataset_type("invalid")
