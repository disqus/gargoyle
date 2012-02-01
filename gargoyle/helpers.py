"""
gargoyle.helpers
~~~~~~~~~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpRequest
from django.utils import simplejson

import datetime
import uuid


class MockRequest(HttpRequest):
    """
    A mock request object which stores a user
    instance and the ip address.
    """
    def __init__(self, user=None, ip_address=None):
        from django.contrib.auth.models import AnonymousUser

        self.user = user or AnonymousUser()
        self.GET = {}
        self.POST = {}
        self.COOKIES = {}
        self.META = {
            'REMOTE_ADDR': ip_address,
        }


class BetterJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return obj.hex
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        elif isinstance(obj, (set, frozenset)):
            return list(obj)
        return super(BetterJSONEncoder, self).default(obj)


def dumps(value, **kwargs):
    return simplejson.dumps(value, cls=BetterJSONEncoder, **kwargs)
