from gargoyle import gargoyle
from gargoyle.conditions import ModelConditionSet, RequestConditionSet, Percent, String, Boolean

from django.contrib.auth.models import AnonymousUser, User
from django.core.validators import validate_ipv4_address

class UserConditionSet(ModelConditionSet):
    percent = Percent()
    username = String()
    is_anonymous = Boolean(label='Anonymous')
    is_staff = Boolean(label='Staff')
    is_superuser = Boolean(label='Superuser')

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
