import datetime

from django.db import models
from django.http import HttpRequest
from django.utils.translation import ugettext_lazy as _

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
        verbose_name = _('switch')
        verbose_name_plural = _('switches')
        
    
    def __unicode__(self):
        return u"%s=%s" % (self.key, self.value)
    
    def to_dict(self):
        data = {
            'key': self.key,
            'status': self.status,
            'label': self.label,
            'description': self.description,
            'conditions': [],
        }

        last = None
        for condition_set_id, group, field, value, exclude in self.get_active_conditions():
            if not last or last['id'] != condition_set_id:
                if last:
                    data['conditions'].append(last)

                last = {
                    'id': condition_set_id,
                    'label': group,
                    'conditions': []
                }

            last['conditions'].append((field.name, value, field.display(value), exclude))
        if last:
            data['conditions'].append(last)

        return data

    def add_condition(self, condition_set, field_name, condition, exclude=False, commit=True):
        from gargoyle import gargoyle
        
        condition_set = gargoyle.get_condition_set_by_id(condition_set)

        assert isinstance(condition, basestring), 'conditions must be strings'

        namespace = condition_set.get_namespace()

        if namespace not in self.value:
            self.value[namespace] = {}
        if field_name not in self.value[namespace]:
            self.value[namespace][field_name] = []
        if condition not in self.value[namespace][field_name]:
            self.value[namespace][field_name].append((exclude and EXCLUDE or INCLUDE, condition))

        if commit:
            self.save()
    
    def remove_condition(self, condition_set, field_name, condition, commit=True):
        from gargoyle import gargoyle

        condition_set = gargoyle.get_condition_set_by_id(condition_set)

        namespace = condition_set.get_namespace()

        if namespace not in self.value:
            return
            
        if field_name not in self.value[namespace]:
            return

        self.value[namespace][field_name] = [c for c in self.value[namespace][field_name] if c[1] != condition]

        if commit:
            self.save()

    def clear_conditions(self, condition_set, field_name=None, commit=True):
        from gargoyle import gargoyle

        condition_set = gargoyle.get_condition_set_by_id(condition_set)

        namespace = condition_set.get_namespace()

        if namespace not in self.value:
            return
        
        if not field_name:
            del self.value[namespace]
        elif field_name not in self.value[namespace]:
            return
        else:
            del self.value[namespace][field_name]
        
        if commit:
            self.save()

    def get_active_conditions(self):
        "Returns groups of lists of active conditions"
        from gargoyle import gargoyle

        for condition_set in sorted(gargoyle.get_condition_sets(), key=lambda x: x.get_group_label()):
            ns = condition_set.get_namespace()
            condition_set_id = condition_set.get_id()
            if ns in self.value:
                group = condition_set.get_group_label()
                for name, field in condition_set.fields.iteritems():
                    for value in self.value[ns].get(name, []):
                        try:
                            yield condition_set_id, group, field, value[1], value[0] == EXCLUDE
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