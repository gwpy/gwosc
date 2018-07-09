#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) Duncan Macleod (2017)
#
# This file is part of GWOSC
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

"""Setup the GWOSC package
"""

import sys

from setuptools import (setup, find_packages)

import versioneer

__version__ = versioneer.get_version()

# setup dependencies for testing (only if we are actually testing)
if set(('test',)).intersection(sys.argv):
    setup_requires = ['pytest_runner']
else:
    setup_requires = []

# get long description from README
with open('README.md', 'rb') as f:
    longdesc = f.read().decode().strip()

# run setup
setup(
    name='gwosc',
    version=__version__,
    packages=find_packages(),
    description="A python interface to the GW Open Science data archive",
    long_description=longdesc,
    long_description_content_type='text/markdown',
    author='Duncan Macleod',
    author_email='duncan.macleod@ligo.org',
    url='https://github.com/gwpy/gwosc',
    license='MIT',
    setup_requires=setup_requires,
    install_requires=['six>=1.9.0'],
    tests_require=['pytest>=2.8'],
    extras_require={
        'docs': ['sphinx', 'sphinx_rtd_theme', 'numpydoc'],
    },
    cmdclass=versioneer.get_cmdclass(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: MIT License',
    ],
)
