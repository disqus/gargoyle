from django.conf import settings

from gargoyle.models import SwitchManager, Switch

gargoyle = SwitchManager(Switch, key='key', value='value', instances=True,
    auto_create=getattr(settings, 'GARGOYLE_AUTO_CREATE', True))
