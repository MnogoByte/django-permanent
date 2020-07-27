#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name='django-permanent',
    version='1.1.7',
    description='Yet another approach to provide soft (logical) delete or masking (thrashing) django models instead of deleting them physically from db.',
    author='Mikhail Antonov',
    author_email='atin65536@gmail.com',
    long_description=open('README.rst').read(),
    url='https://github.com/MnogoByte/django-permanent',
    packages=find_packages(),
    install_requires=["Django>=1.7.0"],
    keywords=['django', 'delete', 'undelete', 'safedelete', 'remove', 'restore', 'softdelete', 'logicaldelete', 'trash'],
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
    ],
    tests_require=["Django>=1.7.0"],
    test_suite='runtests.runtests',
    license="BSD"
)
