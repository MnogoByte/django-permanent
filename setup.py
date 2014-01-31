# -*- coding: utf-8 -*-
from setuptools import setup


setup(name='django-permanent',
      version='1.0.0',
      description='Yet another approach to provide soft (logical) delete or masking (thrashing) django models instead of deleting them physically from db.',
      author='Alexander Klimenko',
      author_email='alex@erix.ru',
      long_description = open('README.rst').read(),
      url='https://github.com/meteozond/django-permanent',
      packages=['django_permanent'],
      install_requires=["Django>=1.6.0"],
      classifiers=[
            "Framework :: Django",
            "Intended Audience :: Developers",
            "Intended Audience :: System Administrators",
            "Operating System :: OS Independent",
            "Topic :: Software Development"
      ],
      tests_require=["Django>=1.6.0", "django-model-utils"],
      test_suite='runtests.runtests',
      license="BSD")
