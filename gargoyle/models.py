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

GLOBAL_NAMESPACE = 'global'

INCLUDE = 'i'
EXCLUDE = 'e'

class Switch(models.Model):
    """
    
    ``value`` is stored with by type label, and then by column:
    
    {
      disable: bool,
      namespace: {
          id: [[INCLUDE, 0, 50], [INCLUDE, 'string']] // 50% of users
      }
    }
    """
    
    key = models.CharField(max_length=32, primary_key=True)
    value = JSONField(default="{\"%s\": false}" % GLOBAL_NAMESPACE)
    label = models.CharField(max_length=32, null=True)
    date_created = models.DateTimeField(default=datetime.datetime.now)
    description = models.TextField(null=True)
    
    class Meta:
        permissions = (
            ("can_view", "Can view"),
        )
        
    
    def __unicode__(self):
        return u"%s=%s" % (self.key, self.value)
    
    def save(self, *args, **kwargs):
        super(Switch, self).save(*args, **kwargs)
        gargoyle._populate(reset=True)
    
    def delete(self, *args, **kwargs):
        super(Switch, self).delete(*args, **kwargs)
        gargoyle._populate(reset=True)
    
    def to_dict(self):
        data = {
            'key': self.key,
            'status': self.status,
            'label': self.label,
            'description': self.description,
            'conditions': {}
        }

        for group, field, value, is_exclude in self.get_active_conditions():
            if group not in data['conditions']:
                data['conditions'][group] = [(field.name, value, field.display(value), is_exclude)]
            else:
                data['conditions'][group].append((field.name, value, field.display(value), is_exclude))

        return data
    
    def get_status(self):
        if self.value.get(GLOBAL_NAMESPACE) is False:
            return DISABLED
        elif self.value.get(GLOBAL_NAMESPACE):
            return GLOBAL
        else:
            return SELECTIVE
            
    status = property(get_status)

    def add_condition(self, switch_id, field_name, condition, commit=True):
        assert len(condition) == 2
        
        if condition[0] not in (INCLUDE, EXCLUDE):
            raise ValueError('Condition must be a list who\'s first item is INCLUDE or EXCLUDE')

        switch = gargoyle.get_switch_by_id(switch_id)
        namespace = switch.get_namespace()
        if namespace not in self.value:
            self.value[namespace] = {}
        if field_name not in self.value[namespace]:
            self.value[namespace][field_name] = []
        if condition not in self.value[namespace][field_name]:
            self.value[namespace][field_name].append(condition)
        if commit:
            self.save()
    
    def remove_condition(self, switch_id, field_name, condition, commit=True):
        switch = gargoyle.get_switch_by_id(switch_id)
        namespace = switch.get_namespace()
        if namespace not in self.value:
            return
        if field_name not in self.value[namespace]:
            return
        self.value[namespace][field_name] = [c for c in self.value[namespace][field_name] if c[1] != condition]
        if commit:
            self.save()

    def get_active_conditions(self):
        "Returns groups of lists of active conditions"
        for switch in sorted(gargoyle._registry.itervalues(), key=lambda x: x.get_group_label()):
            ns = switch.get_namespace()
            if ns in self.value:
                group = switch.get_group_label()
                for name, field in switch.fields.iteritems():
                    for value in self.value[ns].get(name, []):
                        try:
                            yield group, field, value[1], value[0] == EXCLUDE
                        except TypeError:
                            continue

class SwitchManager(ModelDict):
    _registry = {}
    
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
        elif conditions.get(GLOBAL_NAMESPACE):
            return True
        elif conditions.get(GLOBAL_NAMESPACE) is False:
            return False

        if instances:
            # HACK: support request.user by swapping in User instance
            instances = list(instances)
            for v in instances:
                if isinstance(v, HttpRequest) and hasattr(v, 'user'):
                    instances.append(v.user)

            for instance in instances:
                # check each switch to see if it can execute
                for switch in self._registry.itervalues():
                    if switch.can_execute(instance):
                        if switch.is_active(instance, conditions):
                            return True

        return False
    
    def register(self, switch):
        if callable(switch):
            switch = switch()
        self._registry[switch.get_id()] = switch

    def get_switch_by_id(self, switch_id):
        return self._registry[switch_id]

    def get_all_conditions(self):
        "Returns groups of lists of conditions"
        for switch in sorted(self._registry.itervalues(), key=lambda x: x.get_group_label()):
            group = unicode(switch.get_group_label())
            for field in switch.fields.itervalues():
                yield group, switch.get_id(), field
gargoyle = SwitchManager(Switch, key='key', value='value', instances=True)