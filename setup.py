#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(name='django-permanent',
      version='1.0.8',
      description='Yet another approach to provide soft (logical) delete or masking (thrashing) django models instead of deleting them physically from db.',
      author='Alexander Klimenko',
      author_email='alex@erix.ru',
      long_description = open('README.rst').read(),
      url='https://github.com/meteozond/django-permanent',
      packages=find_packages(),
      install_requires=["Django>=1.6.0"],
      keywords = ['django', 'delete', 'undelete', 'safedelete', 'remove', 'restore', 'softdelete', 'logicaldelete', 'trash'],
      classifiers=[
            "Framework :: Django",
            "Intended Audience :: Developers",
            "Intended Audience :: System Administrators",
            "Operating System :: OS Independent",
            "Topic :: Software Development",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 2.7",
            "Development Status :: 4 - Beta",
            "License :: OSI Approved :: BSD License",
      ],
      tests_require=["Django>=1.6.0", "django-model-utils"],
      test_suite='runtests.runtests',
      license="BSD")
