from django.conf.urls.defaults import *

import nexus

nexus.autodiscover()

urlpatterns = patterns('',
    url(r'', include(nexus.site.urls)),
)
