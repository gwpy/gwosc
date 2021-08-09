# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2018-2021)
# SPDX-License-Identifier: MIT

"""Utilities for URL handling
"""

import re
from os.path import (basename, splitext)

from .utils import segments_overlap

# GWOSC filename re
URL_REGEX = re.compile(
    r"\A((.*/)*(?P<obs>[^/]+)-"
    r"(?P<ifo>[A-Z][0-9])_(L|GW)OSC_"
    r"((?P<tag>[^/]+)_)?"
    r"(?P<samp>\d+(KHZ)?)_"
    r"[RV](?P<version>\d+)-"
    r"(?P<strt>[^/]+)-"
    r"(?P<dur>[^/\.]+)\."
    r"(?P<ext>[^/]+))\Z"
)

VERSION_REGEX = re.compile(r'[RV]\d+')


def sieve(urllist, segment=None, **match):
    """Sieve a list of GWOSC URL metadata dicts based on key, value pairs

    Parameters
    ----------
    urllist : `list` of `dict`
        the ``'strain'`` metadata list, as retrieved from the GWOSC
        server

    segment : `tuple` of `int`
        a ``[start, stop)`` GPS segment against which to check overlap
        for each URL

    **match
        other keywords match **exactly** against the corresponding key
        in the `dict` for each URL

    Yields
    ------
    dict :
        each URL dict that matches the parameters is yielded, in the same
        order as the input ``urllist``
    """
    # remove null keys
    match = {key: value for key, value in match.items() if value is not None}

    # sieve
    for urlmeta in urllist:
        try:
            if any(match[key] != urlmeta[key] for key in match):
                continue
        except KeyError as exc:
            raise TypeError(
                "unrecognised match parameter: {}".format(str(exc))
            )
        if segment:  # check overlap
            _start = urlmeta["GPSstart"]
            thisseg = (_start, _start + urlmeta["duration"])
            if not segments_overlap(segment, thisseg):
                continue
        yield urlmeta


def _match_url(
        url,
        detector=None,
        start=None,
        end=None,
        tag=None,
        sample_rate=None,
        version=None,
        duration=None,
        ext=None,
):
    """Match a URL against requested parameters

    Returns
    -------
    None
        if the URL doesn't match the request

    tag, version : `str`, `int`
        if the URL matches the request

    Raises
    ------
    StopIteration
        if the start time of the URL is _after_ the end time of the
        request
    """
    reg = URL_REGEX.match(basename(url)).groupdict()
    for param, regvar in (
        (detector, reg['ifo']),
        (tag, reg['tag']),
        (version, int(reg['version'])),
        (sample_rate, float(reg["samp"].rstrip("KHZ")) * 1024),
        (duration, float(reg["dur"]) != duration),
        (ext, reg["ext"] != ext),
    ):
        # if param was given and the regex value doesn't match, ignore this url
        if param and regvar != param:
            return

    # match times
    if end is not None:
        gps = int(reg['strt'])
        if gps >= end:  # too late
            return

    if start is not None:
        gps = int(reg['strt'])
        dur = int(reg['dur'])
        if gps + dur <= start:  # too early
            return

    return reg['tag'], int(reg['version'])


def match(
        urls,
        detector=None,
        start=None,
        end=None,
        tag=None,
        sample_rate=None,
        version=None,
        duration=None,
        ext=None,
):
    """Match GWOSC URLs for a given [start, end) interval

    Parameters
    ----------
    urls : `list` of `str`
        List of URL paths

    start : `int`
        GPS start time of match interval

    end : `int`
        GPS end time of match interval

    tag : `str`, optional
        URL tag to match, e.g. ``'CLN'``

    version : `int`, optional
        Data release version to match, defaults to highest available
        version

    Returns
    -------
    urls : `list` of `str`
        A sub-list of the input, based on matching, if no URLs are matched,
        the return will be empty ``[]``.
    """
    matched = {}
    matched_tags = set()

    # sort URLs by duration, then start time, then ...
    urls = sorted(
        urls, key=lambda u: splitext(basename(u))[0].split('-')[::-1],
    )

    # format version request
    if VERSION_REGEX.match(str(version)):
        version = version[1:]
    if version is not None:
        version = int(version)

    # loop URLS
    for url in urls:
        m = _match_url(
            url,
            detector=detector,
            start=start,
            end=end,
            tag=tag,
            sample_rate=sample_rate,
            version=version,
            duration=duration,
            ext=ext,
        )
        if m is None:
            continue

        mtag, mvers = m
        matched_tags.add(mtag)
        matched.setdefault(mvers, [])
        matched[mvers].append(url)

    # if multiple file tags found, and user didn't specify, error
    if len(matched_tags) > 1:
        tags = ', '.join(map(repr, matched_tags))
        raise ValueError("multiple GWOSC URL tags discovered in dataset, "
                         "please select one of: {}".format(tags))

    # extract highest version
    try:
        return matched[max(matched)]
    except ValueError:  # no matched files
        return []
