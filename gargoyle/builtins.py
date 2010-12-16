from gargoyle.models import gargoyle
from gargoyle.switches import ModelSwitch, RequestSwitch

from django.contrib.auth.models import User

class UserRequestSwitch(RequestSwitch):
    def get_type_label(self):
        return 'User'

    def is_active_among(self, key, request, values):
        return gargoyle.is_active(key, request.user)

gargoyle.register(ModelSwitch(User, 'is_authenticated'))
gargoyle.register(ModelSwitch(User, 'id'))
gargoyle.register(ModelSwitch(User, 'username'))
gargoyle.register(ModelSwitch(User, 'is_staff'))

gargoyle.register(UserRequestSwitch())