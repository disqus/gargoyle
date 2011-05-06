from django.conf.urls.defaults import *

def foo(request):
    from django.http import HttpResponse
    return HttpResponse()

urlpatterns = patterns('',
    url('', foo, name='gargoyle_test_foo'),
)
