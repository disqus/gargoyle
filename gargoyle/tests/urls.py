from django.conf.urls.defaults import *

def foo(request):
    from django.http import HttpResponse
    return HttpResponse()

urlpatterns = patterns('',
    ('', foo),
)
