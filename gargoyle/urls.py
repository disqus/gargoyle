import os
import re

from django.conf.urls.defaults import *

GARGOYLE_ROOT = os.path.dirname(__file__)
print GARGOYLE_ROOT
print "test"

urlpatterns = patterns('gargoyle.views',
    url(r'^media/(?P<path>.+)?/$', 'django.views.static.serve',
        {'document_root': os.path.join(GARGOYLE_ROOT, 'media')}, name='gargoyle-media'),

    url(r'^$', 'index', name='gargoyle'),
)