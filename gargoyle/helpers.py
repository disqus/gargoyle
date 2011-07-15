"""
gargoyle.helpers
~~~~~~~~~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from django.http import HttpRequest

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