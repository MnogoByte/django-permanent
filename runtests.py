import os
import sys

import django
import django.conf


DEFAULT_SETTINGS = dict(
    INSTALLED_APPS=(
        'django_permanent',
    ),
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3'
        }
    },
    MIDDLEWARE_CLASSES=[]
)


def runtests(*test_args):
    if not django.conf.settings.configured:
        django.conf.settings.configure(**DEFAULT_SETTINGS)
    if hasattr(django, 'setup'):
        django.setup()
    if not test_args:
        test_args = ['django_permanent.tests']

    parent = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent)
    from django.test.runner import DiscoverRunner
    failures = DiscoverRunner(verbosity=1, interactive=True, failfast=True).run_tests(test_args)
    sys.exit(failures)

if __name__ == '__main__':
    runtests()
