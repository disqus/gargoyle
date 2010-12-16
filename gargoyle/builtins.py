from gargoyle.models import gargoyle
from gargoyle.switches import ModelSwitch, RequestSwitch, Percent, String, Boolean

from django.contrib.auth.models import User

class UserSwitch(ModelSwitch):
    percent = Percent()
    username = String()
    is_authenticated = Boolean(label='Anonymous')

    def get_field_value(self, instance, field_name):
        if field_name == 'percent':
            field_name = 'id'
        return super(UserSwitch, self).get_field_value(instance, field_name)

gargoyle.register(UserSwitch(User))

class IPAddressSwitch(RequestSwitch):
    percent = Percent()
    ip_address = String()

gargoyle.register(IPAddressSwitch())
