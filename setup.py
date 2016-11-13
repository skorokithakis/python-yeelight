#!/usr/bin/env python

import sys
from yeelight import __version__
assert sys.version >= '2.7', "Requires Python v2.7 or above."
from setuptools import setup

classifiers = [
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

setup(
    name="yeelight",
    version=__version__,
    author="Stavros Korokithakis",
    author_email="hi@stavros.io",
    url="https://gitlab.com/stavros/python-yeelight/",
    description="A library for controlling YeeLight RGB bulbs.",
    long_description="A library for controlling YeeLight RGB bulbs through WiFi.",
    license="BSD",
    classifiers=classifiers,
    packages=["yeelight"],
    test_suite='yeelight.tests',
    tests_require=['flake8'],
)
