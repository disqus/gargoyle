"""
gargoyle.builtins
~~~~~~~~~~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from gargoyle import gargoyle
from gargoyle.conditions import ModelConditionSet, RequestConditionSet, Percent, String, Boolean, \
                                ConditionSet, OnOrAfterDate

from django.contrib.auth.models import AnonymousUser, User
from django.core.validators import validate_ipv4_address

import socket

class UserConditionSet(ModelConditionSet):
    username = String()
    email = String()
    is_anonymous = Boolean(label='Anonymous')
    is_staff = Boolean(label='Staff')
    is_superuser = Boolean(label='Superuser')
    date_joined = OnOrAfterDate(label='Joined on or after')

    def can_execute(self, instance):
        return isinstance(instance, (User, AnonymousUser))

    def is_active(self, instance, conditions):
        """
        value is the current value of the switch
        instance is the instance of our type
        """
        if isinstance(instance, User):
            return super(UserConditionSet, self).is_active(instance, conditions)
        
        # HACK: allow is_authenticated to work on AnonymousUser
        condition = conditions.get(self.get_namespace(), {}).get('is_anonymous')
        return bool(condition)

gargoyle.register(UserConditionSet(User))

class IPAddress(String):
    def clean(self, value):
        validate_ipv4_address(value)
        return value

class IPAddressConditionSet(RequestConditionSet):
    percent = Percent()
    ip_address = IPAddress(label='IP Address')

    def get_namespace(self):
        return 'ip'

    def get_field_value(self, instance, field_name):
        # XXX: can we come up w/ a better API?
        # Ensure we map ``percent`` to the ``id`` column
        if field_name == 'percent':
            return sum([int(x) for x in instance.META['REMOTE_ADDR'].split('.')])
        elif field_name == 'ip_address':
            return instance.META['REMOTE_ADDR']
        return super(IPAddressConditionSet, self).get_field_value(instance, field_name)

    def get_group_label(self):
        return 'IP Address'

gargoyle.register(IPAddressConditionSet())

class HostConditionSet(ConditionSet):
    hostname = String()

    def get_namespace(self):
        return 'host'
    
    def can_execute(self, instance):
        return instance is None
    
    def get_field_value(self, instance, field_name):
        if field_name == 'hostname':
            return socket.gethostname()

    def get_group_label(self):
        return 'Host'

gargoyle.register(HostConditionSet())
