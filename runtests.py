# -*- encoding: utf-8 -*-

import os, sys
import django
from django.conf import settings


DEFAULT_SETTINGS = dict(
    INSTALLED_APPS=(
        'django_permanent',
        'tests',
    ),
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3'
        }
    }
)


def runtests(*test_args):
    if not settings.configured:
        settings.configure(**DEFAULT_SETTINGS)
    if hasattr(django, 'setup'):
        django.setup()
    if not test_args:
        test_args = ['django_permanent', 'tests']

    parent = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent)
    from django.test.simple import DjangoTestSuiteRunner
    failures = DjangoTestSuiteRunner(verbosity=1, interactive=True, failfast=False).run_tests(test_args)
    sys.exit(failures)

if __name__ == '__main__':
    runtests()
