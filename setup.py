# -*- coding: utf-8 -*-
from distutils.core import setup


setup(name='django-permanent',
      version='0.1.4',
      description='Yet another approach to provide soft (logical) delete or masking (thrashing) django models instead of deleting them physically from db.',
      author='Alexander Klimenko',
      author_email='alex@erix.ru',
      long_description = open('README.rst').read(),
      url='https://github.com/meteozond/django-permanent',
      packages=['django_permanent'],
      install_requires=['django_model_utils==1.5.0'],
      classifiers=[
            "Framework :: Django",
            "Intended Audience :: Developers",
            "Intended Audience :: System Administrators",
            "Operating System :: OS Independent",
            "Topic :: Software Development"
      ],
      license="BSD",)
