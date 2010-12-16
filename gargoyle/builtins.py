from gargoyle.models import gargoyle
from gargoyle.switches import ModelSwitch

from django.contrib.auth.models import User

gargoyle.register(ModelSwitch(User, 'is_authenticated'))
gargoyle.register(ModelSwitch(User, 'id'))
gargoyle.register(ModelSwitch(User, 'username'))
gargoyle.register(ModelSwitch(User, 'is_staff'))
