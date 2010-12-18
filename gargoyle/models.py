import datetime

from django.db import models
from django.http import HttpRequest

from jsonfield import JSONField
from modeldict import ModelDict

DISABLED  = 1
SELECTIVE = 2
GLOBAL    = 3

INCLUDE = 'i'
EXCLUDE = 'e'

class Switch(models.Model):
    """
    
    ``value`` is stored with by type label, and then by column:
    
    {
      namespace: {
          id: [[INCLUDE, 0, 50], [INCLUDE, 'string']] // 50% of users
      }
    }
    """
    
    STATUS_CHOICES = (
        (DISABLED, 'Disabled'),
        (SELECTIVE, 'Selective'),
        (GLOBAL, 'Global'),
    )
    
    key = models.CharField(max_length=32, primary_key=True)
    value = JSONField(default="{}")
    label = models.CharField(max_length=32, null=True)
    date_created = models.DateTimeField(default=datetime.datetime.now)
    description = models.TextField(null=True)
    status = models.PositiveSmallIntegerField(default=DISABLED, choices=STATUS_CHOICES)

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

    def add_condition(self, condition_set, field_name, condition, exclude=False, commit=True):
        if exclude:
            condition = [EXCLUDE, condition]
        else:
            condition = [INCLUDE, condition]
        
        condition_set = gargoyle.get_condition_set_by_id(condition_set)

        namespace = condition_set.get_namespace()

        if namespace not in self.value:
            self.value[namespace] = {}
        if field_name not in self.value[namespace]:
            self.value[namespace][field_name] = set()
        self.value[namespace][field_name].add(condition)

        if commit:
            self.save()
    
    def remove_condition(self, condition_set, field_name, condition, commit=True):
        condition_set = gargoyle.get_condition_set_by_id(condition_set)

        namespace = condition_set.get_namespace()

        if namespace not in self.value:
            return
        if field_name not in self.value[namespace]:
            return

        self.value[namespace][field_name] = [c for c in self.value[namespace][field_name] if c[1] != condition]

        if commit:
            self.save()

    def get_active_conditions(self):
        "Returns groups of lists of active conditions"
        for condition_set in sorted(gargoyle.get_condition_sets(), key=lambda x: x.get_group_label()):
            ns = condition_set.get_namespace()
            if ns in self.value:
                group = condition_set.get_group_label()
                for name, field in condition_set.fields.iteritems():
                    for value in self.value[ns].get(name, set()):
                        try:
                            yield group, field, value[1], value[0] == EXCLUDE
                        except TypeError:
                            continue

class SwitchManager(ModelDict):
    _registry = {}
    
    def _populate(self, *args, **kwargs):
        def coerce_lists_to_sets(chunk):
            if isinstance(chunk, dict):
                for k, v in chunk.iteritems():
                    yield k, coerce_lists_to_sets(v)
            elif isinstance(chunk, (list, tuple)):
                yield set(chunk)
            else:
                yield chunk
        
        cache = super(SwitchManager, self)._populate(*args, **kwargs)
        return coerce_lists_to_sets(cache)
    
    def is_active(self, key, *instances):
        """
        ``gargoyle.is_active('my_feature', request)``
        """
        
        try:
            switch = self[key]
        except KeyError:
            return False

        if switch.status == GLOBAL:
            return True
        elif switch.status == DISABLED:
            return False

        conditions = switch.value
        if not conditions:
            return True

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
    
    def register(self, condition_set):
        if callable(condition_set):
            condition_set = condition_set()
        self._registry[condition_set.get_id()] = condition_set

    def get_condition_set_by_id(self, switch_id):
        return self._registry[switch_id]

    def get_condition_sets(self):
        return self._registry.itervalues()

    def get_all_conditions(self):
        "Returns groups of lists of conditions"
        for condition_set in sorted(self.get_condition_sets(), key=lambda x: x.get_group_label()):
            group = unicode(condition_set.get_group_label())
            for field in condition_set.fields.itervalues():
                yield group, condition_set.get_id(), field
gargoyle = SwitchManager(Switch, key='key', value='value', instances=True)