# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

NAME = 'openslides-votecollector'
VERSION = '1.0.4'
DESCRIPTION = 'VoteCollector Plugin for OpenSlides'


with open('README.rst') as readme:
    long_description = readme.read()


with open('requirements_production.txt') as requirements_production:
    install_requires = requirements_production.readlines()


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    author='VoteCollector Plugin team, see AUTHORS',
    author_email='support@openslides.org',
    url='https://github.com/OpenSlides/openslides-votecollector',
    keywords='OpenSlides',
    classifiers = [
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires)
