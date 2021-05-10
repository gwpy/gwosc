# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2018-2021)
# SPDX-License-Identifier: MIT

from os.path import basename

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'


def url_segment(url):
    """Return the GPS segment covered by a URL following T050017

    Parameters
    ---------
    filename : `str`
        the path name of a file

    Returns
    -------
    segment : `tuple` of `int`
        the ``[start, stop)`` GPS interval covered by the given URL

    Notes
    -----
    `LIGO-T050017 <https://dcc.ligo.org/LIGO-T050017/public>`_ declares
    a filenaming convention that includes documenting the GPS start integer
    and integer duration of a file, see that document for more details.
    """
    base = basename(url)
    _, _, s, e = base.split('-')
    s = int(s)
    e = int(e.split('.')[0])
    return s, s + e


def url_overlaps_segment(url, segment):
    """Returns True if a URL overlaps a [start, stop) GPS interval

    Parameters
    ----------
    url : `str`
        the URL of a file

    segment : `tuple` of `int`
        the ``[start, stop)`` GPS interval to check against

    Returns
    -------
    overlap? : `bool`
        `True` if the GPS interval for the URL matches that given,
        otherwise `False`
    """
    useg = url_segment(url)
    return segments_overlap(useg, segment)


def urllist_extent(urls):
    """Returns the GPS `[start, end)` interval covered by a list or URLs

    Parameters
    ----------
    urls : `iterable` of `str`
        the list of URLs

    Returns
    -------
    a, b : 2-`tuple` of int`
        the GPS extent of the URL list
    """
    segs = map(url_segment, urls)
    starts, ends = zip(*segs)
    return min(starts), max(ends)


def strain_extent(strain):
    """Returns the GPS `[start, end)` interval covered by a strain meta dict
    """
    starts, ends = zip(*[
        (meta["GPSstart"], meta["GPSstart"] + meta["duration"]) for
        meta in strain
    ])
    return min(starts), max(ends)


def full_coverage(urls, segment):
    """Returns True if the list of URLS completely covers a GPS interval

    The URL list is presumed to be contiguous, so this just checks that
    the first URL (by GPS timestamp) and the last URL can form a segment
    that overlaps that given.
    """
    if not urls:
        return False
    # sort URLs by GPS timestamp
    a, b = urllist_extent(urls)
    return a <= segment[0] and b >= segment[1]


def segments_overlap(a, b):
    """Returns True if GPS segment ``a`` overlaps GPS segment ``b``
    """
    return (a[1] > b[0]) and (a[0] < b[1])
