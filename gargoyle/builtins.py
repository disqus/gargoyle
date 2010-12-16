from gargoyle.models import gargoyle
from gargoyle.switches import ModelSwitch

from django.contrib.auth.models import User

gargoyle.register(ModelSwitch(User, 'is_authenticated'))
