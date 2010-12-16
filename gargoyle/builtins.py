from gargoyle.models import gargoyle
from gargoyle.switches import ModelSwitch, RequestSwitch, Percent, String, Boolean

from django.contrib.auth.models import AnonymousUser, User

class UserSwitch(ModelSwitch):
    percent = Percent()
    username = String()
    is_authenticated = Boolean(label='Anonymous')

    def can_execute(self, instance):
        return isinstance(instance, (User, AnonymousUser))

    def is_active(self, instance, conditions):
        """
        value is the current value of the switch
        instance is the instance of our type
        """
        if isinstance(instance, User):
            return super(UserSwitch, self).is_active(instance, conditions)
        
        # HACK: allow is_authenticated to work on AnonymousUser
        condition = conditions.get(self.model.__name__, {}).get('is_authenticated')
        return bool(condition is False)

gargoyle.register(UserSwitch(User))

class IPAddressSwitch(RequestSwitch):
    percent = Percent()
    ip_address = String()

    def get_namespace(self):
        return 'ip'

    def get_field_value(self, instance, field_name):
        # XXX: can we come up w/ a better API?
        # Ensure we map ``percent`` to the ``id`` column
        if field_name == 'percent':
            return sum([int(x) for x in instance.META['REMOTE_ADDR'].split('.')])
        elif field_name == 'ip_address':
            return instance.META['REMOTE_ADDR']
        return super(IPAddressSwitch, self).get_field_value(instance, field_name)

gargoyle.register(IPAddressSwitch())
