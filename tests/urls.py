"""
:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

try:
    # Django <1.6
    from django.conf.urls.defaults import *
except ImportError:
    # Django >=1.6
    from django.conf.urls import *


def foo(request):
    from django.http import HttpResponse
    return HttpResponse()

urlpatterns = patterns('',
    url('', foo, name='gargoyle_test_foo'),
)
