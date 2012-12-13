#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup script for votecollector.

    :copyright: by Oskar Hahn
    :license: GNU GPL, see LICENSE for more details.
"""
version = '1.0.2'
# for python 2.5 support
## from __future__ import with_statement

from setuptools import setup
from setuptools import find_packages


## with open('README.txt') as file:
    ## long_description = file.read()

setup(
    name='openslides-votecollector',
    description='votecollector for OpenSlides',
    ## long_description=long_description,
    version=version,
    url='https://github.com/OpenSlides/openslides-votecollector',
    author='Oskar Hahn',
    author_email='mail@oshahn.de',
    license='GPL2+',
    packages=find_packages(),
    include_package_data = True,
    classifiers = [
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Other Audience',
        'Framework :: Django',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    setup_requires=[
        'versiontools >= 1.6',
    ],
    install_requires=[
        'openslides==1.3',
    ],
    zip_safe=False,
)
