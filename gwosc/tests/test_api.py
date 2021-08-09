# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2018-2021)
# SPDX-License-Identifier: MIT

"""Tests for :mod:`gwosc.api`
"""

import os.path
from unittest import mock

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
    url = 'https://www.gw-openscience.org/archive/1126257414/1126261510/json/'
    out = api.fetch_json(url)
    assert isinstance(out, dict)
    assert len(out['events']) == 3
    assert sorted(out['events']['GW150914-v1']['detectors']) == ['H1', 'L1']
    assert {'tenyear', 'O1', 'O1_16KHZ', 'history'}.issubset(set(out['runs']))

    # check errors (use legit URL that isn't JSON)
    url2 = os.path.dirname(os.path.dirname(url))
    with pytest.raises(ValueError) as exc:
        api.fetch_json(url2)
    assert str(exc.value).startswith(
        "Failed to parse GWOSC JSON from {!r}: ".format(url2))


def test_fetch_json_local(requests_mock):
    url = 'http://anything'
    requests_mock.get(
        url,
        json={"key": "value"},
    )
    out = api.fetch_json(url)
    assert isinstance(out, dict)
    assert out['key'] == 'value'


@pytest.mark.remote
def test_fetch_dataset_json():
    start = 934000000
    end = 934100000
    out = api.fetch_dataset_json(start, end)
    assert not out['events']
    assert {"tenyear", "S6", "history"}.issubset(set(out['runs']))


@mock.patch('gwosc.api.fetch_json')
def test_fetch_dataset_json_local(fetch):
    start = 934000000
    end = 934100000
    api.fetch_dataset_json(start, end)
    fetch.assert_called_with(
        losc_url('archive/{0}/{1}/json/'.format(start, end)))


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


@mock.patch('gwosc.api.fetch_json')
def test_fetch_run_json_local(fetch):
    api.fetch_run_json('S6', 'L1', 934000000, 934100000)
    fetch.assert_called_with(
        losc_url('archive/links/S6/L1/934000000/934100000/json/'))


@pytest.mark.remote
def test_fetch_cataloglist_json():
    out = api.fetch_cataloglist_json()
    assert "description" in out["GWTC-1-confident"]
    assert "url" in out["GWTC-1-confident"]


@mock.patch("gwosc.api.fetch_json")
def test_fetch_cataloglist_json_local(fetch):
    api.fetch_cataloglist_json()
    fetch.assert_called_with(
        losc_url("eventapi/json/")
    )


@pytest.mark.remote
def test_fetch_catalog_json():
    out = api.fetch_catalog_json("GWTC-1-confident")
    events = out["events"]
    assert events["GW170817-v3"]["GPS"] == 1187008882.4


@mock.patch("gwosc.api.fetch_json")
def test_fetch_catalog_json_local(fetch):
    api.fetch_catalog_json("GWTC-1-confident")
    fetch.assert_called_with(
        losc_url("eventapi/json/GWTC-1-confident/")
    )


@pytest.mark.remote
def test_fetch_event_json():
    out = api.fetch_event_json("GW150914")
    meta = out["events"]["GW150914-v3"]
    assert int(meta["GPS"]) == 1126259462
    assert meta["version"] == 3


@pytest.mark.remote
def test_fetch_event_json_with_hms_suffix():
    out = api.fetch_event_json("GW190930")
    assert list(out["events"].values())[0]["commonName"] == "GW190930_133541"


@pytest.mark.remote
def test_fetch_event_json_version():
    out = api.fetch_event_json("GW150914-v3")["events"]["GW150914-v3"]
    assert out["version"] == 3
    assert out["catalog.shortName"] == "GWTC-1-confident"


@pytest.mark.remote
def test_fetch_event_json_error_no_version():
    with pytest.raises(ValueError):
        api.fetch_event_json("GW150914-v3", version=1)


@pytest.mark.remote
def test_fetch_event_json_error_no_catalog():
    with pytest.raises(ValueError):
        api.fetch_event_json("GW150914-v3", catalog="test")


@pytest.mark.remote
def test_fetch_event_json_error_not_found():
    with pytest.raises(ValueError):
        api.fetch_event_json("blah")


@pytest.mark.remote
def test_fetch_event_json_error_multiple_names():
    with pytest.raises(ValueError) as exc:
        api.fetch_event_json("GW190521")
    assert str(exc.value).startswith("multiple events matched for 'GW190521'")
