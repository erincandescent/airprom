#!/usr/bin/env python3
import setuptools
import sys

if sys.version_info < (3,4):
    sys.exit("Python 3.4 or newer is required.")

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="airprom",
    version="0.0.1",
    author="Erin Shepherd",
    author_email="erin.shepherd@e43.eu",
    description="Super lightweight Prometheus exporter for Philips air purifiers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/erincandescent/airprom",
    install_requires=[
        'py-air-control>=2.0.0',
        ],
    scripts=["airprom.py"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: ISC License",
        "Operating System :: OS Independent",
    ],
)
