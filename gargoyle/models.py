"""
gargoyle.autodiscover()

gargoyle.register(ModelSwitch(Forum, 'slug'))
gargoyle.register(ModelSwitch(Forum, 'id'))

gargoyle.register(RequestSwitch())
"""

from django.db import models

from jsonfield import JSONField
from modeldict import ModelDict

class Switch(models.Model):
    """
    
    ``value`` is stored with by type label, and then by column:
    
    {
      disable: bool,
      user: {
          id: [0, 50] // 50% of users
      }
    }
    """
    
    key = models.CharField(max_length=32, primary_key=True)
    value = JSONField(default="{\"disable\": true}")
    label = models.CharField(max_length=32, null=True)
    description = models.TextField(null=True)
    
    def __unicode__(self):
        return u"%s=%s" % (self.key, self.value)
    
    def save(self, *args, **kwargs):
        super(Switch, self).save(*args, **kwargs)
        gargoyle._populate(reset=True)
    
    def delete(self, *args, **kwargs):
        super(Switch, self).delete(*args, **kwargs)
        gargoyle._populate(reset=True)
    
    def to_dict(self):
        return {
            'key': self.key,
            'status': self.get_status(),
            'active': self.is_active(),
            'label': self.label,
            'description': self.description,
        }
    
    def get_status(self):
        if self.value.get('disable'):
            return 'Disabled'
        elif self.value:
            return 'Selective'
        else:
            return 'Global'

class SwitchManager(ModelDict):
    _registry = {}
    
    def is_active(self, key, *instances):
        """
        ``gargoyle.is_active('my_feature', request)``
        """
        
        values = self.get(key)
        if not values:
            # XXX: option to have default return value?
            return True
        values = values.value
        
        if instances:
            # check each value for this switch against its registered type
            for instance in instances:
                for switch in SwitchManager._registry.get(instance.__class__, []):
                    for value in values.get(switch.get_type_label()):
                        if switch.is_active(instance, value):
                            return True
        # if all other checks failed, look at our global 'disable' flag
        return not values.get('disable')
gargoyle = SwitchManager(Switch, key='key', value='value', instances=True)
