import os
import re

from django.conf.urls.defaults import *

import gargoyle

gargoyle.autodiscover()

GARGOYLE_ROOT = os.path.dirname(__file__)

urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': os.path.join(GARGOYLE_ROOT, 'media'),
        'show_indexes': True,
    }, name='gargoyle-media'),

    url(r'^add/$', 'gargoyle.views.add', name='gargoyle-add'),
    url(r'^update/$', 'gargoyle.views.update', name='gargoyle-update'),
    url(r'^delete/$', 'gargoyle.views.delete', name='gargoyle-delete'),
    url(r'^status/$', 'gargoyle.views.status', name='gargoyle-status'),
    url(r'^conditions/add/$', 'gargoyle.views.add_condition', name='gargoyle-add-condition'),
    url(r'^conditions/remove/$', 'gargoyle.views.remove_condition', name='gargoyle-remove-condition'),
    url(r'^$', 'gargoyle.views.index', name='gargoyle'),
)