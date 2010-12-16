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
        if values.get('disable'):
            return False

        if instances:
            # check each value for this switch against its registered type
            for instance in instances:
                for column, values in values.get(instance.__class__.__name__, {}).iteritems():
                    for switch in self._registry.get((instance.__class__, column), []):
                        if any(switch.is_active(instance, v) for v in values):
                            return True
                
        # if all other checks failed, look at our global 'disable' flag
        return False
    
    def register(self, switch):
        type_ = (switch.get_type(), switch.get_column_label())
        if type_ not in self._registry:
            self._registry[type_] = []
        self._registry[type_].append(switch)

gargoyle = SwitchManager(Switch, key='key', value='value', instances=True)