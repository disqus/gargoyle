from gargoyle.models import gargoyle
from gargoyle.switches import ModelSwitch, RequestSwitch, Percent, String, Boolean

from django.contrib.auth.models import User

class UserSwitch(ModelSwitch):
    percent = Percent()
    username = String()
    is_authenticated = Boolean(label='Anonymous')

gargoyle.register(UserSwitch(User))

class IPAddressSwitch(RequestSwitch):
    percent = Percent()
    ip_address = String()

gargoyle.register(IPAddressSwitch())
