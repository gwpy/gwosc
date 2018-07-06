# -*- coding: utf-8 -*-
# Copyright Duncan Macleod 2017
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
    return (s, s+e)


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


def full_coverage(urls, segment):
    """Returns True if the list of URLS completely covers a GPS interval

    The URL list is presumed to be contiguous, so this just checks that
    the first URL (by GPS timestamp) and the last URL can form a segment
    that overlaps that given.
    """
    if not urls:
        return False
    # sort URLs by GPS timestamp
    urlsegs = [url_segment(u) for u in urls]
    starts, ends = zip(*urlsegs)
    # extract segments for first and last files
    a = min(starts)
    b = max(ends)
    # compare to given segment
    return a <= segment[0] and b >= segment[1]


def segments_overlap(a, b):
    """Returns True if GPS segment ``a`` overlaps GPS segment ``b``
    """
    return (a[1] > b[0]) and (a[0] < b[1])
