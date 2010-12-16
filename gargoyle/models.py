"""
gargoyle.autodiscover()

gargoyle.register(ModelSwitch(Forum, 'slug'))
gargoyle.register(ModelSwitch(Forum, 'id'))

gargoyle.register(RequestSwitch())
"""

from django.db import models
from django.http import HttpRequest

from jsonfield import JSONField
from modeldict import ModelDict

class Switch(models.Model):
    """
    
    ``value`` is stored with by type label, and then by column:
    
    {
      disable: bool,
      class.__name__: {
          id: [0, 50] // 50% of users
      }
    }
    """
    
    key = models.CharField(max_length=32, primary_key=True)
    value = JSONField(default="{\"disable\": true}")
    label = models.CharField(max_length=32, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
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
    _registry = []
    
    def is_active(self, key, *instances):
        """
        ``gargoyle.is_active('my_feature', request)``
        """
        
        conditions = self.get(key)
        if not conditions:
            # XXX: option to have default return value?
            return False

        conditions = conditions.value
        if conditions.get('disable'):
            return False

        if instances:
            # HACK: support request.user by swapping in User instance
            instances = list(instances)
            for v in instances:
                if isinstance(v, HttpRequest) and hasattr(v, 'user'):
                    instances.append(v.user)

            for instance in instances:
                # check each switch to see if it can execute
                for switch in self._registry:
                    if switch.can_execute(instance):
                        if switch.is_active(instance, conditions):
                            return True

        # if all other checks failed, look at our global 'disable' flag
        return not conditions
    
    def register(self, switch):
        if callable(switch):
            switch = switch()
        self._registry.append(switch)
gargoyle = SwitchManager(Switch, key='key', value='value', instances=True)