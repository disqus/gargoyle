"""
gargoyle.autodiscover()

gargoyle.register(ModelSwitch(Forum, 'slug'))
gargoyle.register(ModelSwitch(Forum, 'id'))

gargoyle.register(RequestSwitch())
"""

import datetime

from django.db import models
from django.http import HttpRequest

from jsonfield import JSONField
from modeldict import ModelDict

DISABLED  = 1
SELECTIVE = 2
GLOBAL    = 3

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
    value = JSONField(default="{\"global\": false}")
    label = models.CharField(max_length=32, null=True)
    date_created = models.DateTimeField(default=datetime.datetime.now)
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
            'status': self.status,
            'label': self.label,
            'description': self.description,
        }
    
    def get_status(self):
        if self.value.get('global') is False:
            return DISABLED
        elif self.value.get('global'):
            return GLOBAL
        else:
            return SELECTIVE
            
    status = property(get_status)

    def add_condition(self, namespace, field_name, condition, commit=True):
        if namespace not in self.value:
            self.value[namespace] = {}
        if field_name not in self.value[namespace]:
            self.value[namespace][field_name] = []
        self.value[namespace][field_name].append(condition)
        if commit:
            self.save()
    
    def remove_condition(self, namespace, field_name, condition, commit=True):
        if namespace not in self.value:
            return
        if field_name not in self.value[namespace]:
            return
        self.value[namespace][field_name] = [c for c in self.value[namespace][field_name] if c != condition]
        if commit:
            self.save()

    def get_active_conditions(self):
        "Returns groups of lists of active conditions"
        for switch in sorted(gargoyle._registry, key=lambda x: x.get_group_label()):
            ns = switch.get_namespace()
            if ns in self.value:
                group = switch.get_group_label()
                for field in switch.fields:
                    for value in self.value[ns].get(field.name, []):
                        yield group, field, value
                        "User", field.label, field.render(value)

class SwitchManager(ModelDict):
    _registry = []
    
    def is_active(self, key, *instances):
        """
        ``gargoyle.is_active('my_feature', request)``
        """
        
        try:
            conditions = self[key]
        except KeyError:
            return False

        if not conditions:
            return True

        conditions = conditions.value
        if not conditions:
            return True
        elif conditions.get('global'):
            return True
        elif conditions.get('global') is False:
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

        return False
    
    def register(self, switch):
        if callable(switch):
            switch = switch()
        self._registry.append(switch)

    def get_all_conditions(self):
        "Returns groups of lists of conditions"
        for switch in sorted(self._registry, key=lambda x: x.get_group_label()):
            group = unicode(switch.get_group_label())
            for field in switch.fields.itervalues():
                yield group, switch.get_namespace(), field
gargoyle = SwitchManager(Switch, key='key', value='value', instances=True)