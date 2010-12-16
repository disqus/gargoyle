import os
import re

from django.conf.urls.defaults import *

GARGOYLE_ROOT = os.path.dirname(__file__)

urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': os.path.join(GARGOYLE_ROOT, 'media'),
        'show_indexes': True,
    }, name='gargoyle-media'),

    url(r'^$', 'gargoyle.views.index', name='gargoyle'),
)