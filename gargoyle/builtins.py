from gargoyle.models import gargoyle
from gargoyle.switches import ModelSwitch, RequestSwitch, Percent, String, Boolean

from django.contrib.auth.models import AnonymousUser, User

class UserSwitch(ModelSwitch):
    percent = Percent()
    username = String()
    is_authenticated = Boolean(label='Anonymous')

    def can_execute(self, instance):
        return isinstance(instance, (User, AnonymousUser))

    def get_field_value(self, instance, field_name):
        # XXX: can we come up w/ a better API?
        # Ensure we map ``percent`` to the ``id`` column
        if field_name == 'percent':
            field_name = 'id'
        return super(UserSwitch, self).get_field_value(instance, field_name)

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

gargoyle.register(IPAddressSwitch())
