# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2018-2021)
# SPDX-License-Identifier: MIT

"""GWOSC: a python interface to the GW Open Science data archive
"""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"
__license = "MIT"

try:
    from ._version import version as __version__
except ModuleNotFoundError:  # development mode
    __version__ = ''
