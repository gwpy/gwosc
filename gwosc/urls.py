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

"""Utilities for URL handling
"""

import os.path
import re

# LOSC filename re
URL_REGEX = re.compile(
    r"\A((.*/)*(?P<obs>[^/]+)-"
    r"(?P<ifo>[A-Z][0-9])_LOSC_"
    r"((?P<tag>[^/]+)_)?"
    r"(?P<samp>\d+)_"
    r"(?P<version>V\d+)-"
    r"(?P<strt>[^/]+)-"
    r"(?P<dur>[^/\.]+)\."
    r"(?P<ext>[^/]+))\Z"
)
VERSION_REGEX = re.compile(r'V\d+')


def sieve(urllist, **match):
    """Sieve a list of LOSC URL metadata dicts based on key, value pairs

    This method simply matches keys from the ``match`` keywords with those
    found in the JSON dicts for a file URL returned by the LOSC API.
    """
    if 'sample_rate' in match and 'sampling_rate' not in match:
        match['sampling_rate'] = match.pop('sample_rate')
    for urlmeta in urllist:
        if any(match[key] != urlmeta[key] for key in match):
            continue
        yield urlmeta


def _match_url(url, start=None, end=None, tag=None, version=None):
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
    reg = URL_REGEX.match(os.path.basename(url)).groupdict()
    if (tag and reg['tag'] != tag) or (version and reg['version'] != version):
        return

    # match times
    if end is not None:
        gps = int(reg['strt'])
        if gps >= end:  # too late, stop
            raise StopIteration

    if start is not None:
        gps = int(reg['strt'])
        dur = int(reg['dur'])
        if gps + dur <= start:  # too early
            return

    return reg['tag'], int(reg['version'][1:])


def match(urls, start=None, end=None, tag=None, version=None):
    """Match LOSC URLs for a given [start, end) interval

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
    urls.sort(key=lambda u:
              os.path.splitext(os.path.basename(u))[0].split('-')[::-1])

    # format version request
    if version and not VERSION_REGEX.match(str(version)):
        version = 'V{}'.format(int(version))

    # loop URLS
    for url in urls:
        try:
            m = _match_url(url, start, end, tag=tag, version=version)
        except StopIteration:
            break
        if m is None:
            continue

        mtag, mvers = m
        matched_tags.add(mtag)
        matched.setdefault(mvers, [])
        matched[mvers].append(url)

    # if multiple file tags found, and user didn't specify, error
    if len(matched_tags) > 1:
        tags = ', '.join(map(repr, matched_tags))
        raise ValueError("multiple LOSC URL tags discovered in dataset, "
                         "please select one of: {}".format(tags))

    # extract highest version
    try:
        return matched[max(matched)]
    except ValueError:  # no matched files
        return []
