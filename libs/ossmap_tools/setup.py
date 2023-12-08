#!/usr/bin/env python
# encoding: utf-8

from setuptools import find_packages, setup

setup(
    name="ossmap_tools",
    version="0.1",
    description="Loading network data, implementing different backbone extraction techniques and other common utilities",
    author="Zhouming Wu",
    author_email="wu.zhoum@northeastern.edu",
    license="MIT",
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        "pandas",
        "networkx",
        "fa2",
        "webweb",
        "black",
    ],
    zip_safe=False,
    test_suite="nose.collector",
    tests_require=["nose"],
)
