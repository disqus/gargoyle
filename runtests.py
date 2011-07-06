#!/usr/bin/env python

"""
runtests
~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

import sys
from os.path import dirname, abspath

from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASE_ENGINE='sqlite3',
        DATABASES={
            'default': {
                'ENGINE': 'sqlite3',
            },
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.admin',
            'django.contrib.sessions',
            'django.contrib.sites',

            # Included to fix Disqus' test Django which solves IntegrityMessage case
            'django.contrib.contenttypes',
            'gargoyle',
            'south',

            'tests',
        ],
        ROOT_URLCONF='',
        DEBUG=False,
        TEMPLATE_DEBUG=True,
        GARGOYLE_SWITCH_DEFAULTS = {
            'active_by_default': {
              'is_active': True,
              'label': 'Default Active',
              'description': 'When you want the newness',
            },
            'inactive_by_default': {
              'is_active': False,
              'label': 'Default Inactive',
              'description': 'Controls the funkiness.',
            },
        },
    )
    
from django.test.simple import run_tests

def runtests(*test_args):
    if 'south' in settings.INSTALLED_APPS:
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()

    if not test_args:
        test_args = ['tests']
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)
    failures = run_tests(test_args, verbosity=1, interactive=True)
    sys.exit(failures)

if __name__ == '__main__':
    runtests(*sys.argv[1:])