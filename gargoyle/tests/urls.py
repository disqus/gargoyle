"""
gargoyle.tests.urls
~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from django.conf.urls.defaults import *

def foo(request):
    from django.http import HttpResponse
    return HttpResponse()

urlpatterns = patterns('',
    url('', foo, name='gargoyle_test_foo'),
)
