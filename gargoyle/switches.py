# TODO: i18n
# Credit to Haystack for abstraction concepts

from django.http import HttpRequest

class Field(object):
    def __init__(self, label=None):
        self.label = label
        self.set_instance_name(None)
    
    def set_instance_name(self, instance_name):
        self.instance_name = instance_name
    
    def is_active(self, condition, value):
        return condition == value

class Boolean(Field):
    def is_active(self, condition, value):
        return bool(value)

class Choice(Field):
    def __init__(self, choices, **kwargs):
        self.choices = choices
        super(Choice, self).__init__(**kwargs)

    def is_active(self, condition, value):
        return value in self.choices

class Range(Field):
    def is_active(self, condition, value):
        return value >= condition[0] and value <= condition[1]

class Percent(Field):
    def is_active(self, condition, value):
        mod = value % 100
        return mod >= condition[0] and mod <= condition[1]

class String(Field):
    pass

class SwitchBase(type):
    def __new__(cls, name, bases, attrs):
        attrs['fields'] = {}
        
        # Inherit any fields from parent(s).
        try:
            parents = [b for b in bases if issubclass(b, Switch)]
            
            for p in parents:
                fields = getattr(p, 'fields', None)
                
                if fields:
                    attrs['fields'].update(fields)
        except NameError:
            pass

        for field_name, obj in attrs.items():
            if isinstance(obj, Field):
                field = attrs.pop(field_name)
                field.set_instance_name(field_name)
                attrs['fields'][field_name] = field
        
        return super(SwitchBase, cls).__new__(cls, name, bases, attrs)

class Switch(object):
    __metaclass__ = SwitchBase

    def __repr__(self):
        return '<%s>' % (self.__class__.__name__,)

    def can_execute(self, instance):
        return True

class ModelSwitch(Switch):
    def __init__(self, model):
        self.model = model

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.model.__name__)
        
    def can_execute(self, instance):
        return isinstance(instance, self.model)
    
    def get_type(self):
        return self.model
    
    def get_group_label(self):
        return self.model._meta.verbose_name

    def get_field_value(self, instance, field_name):
        value = getattr(instance, field_name)
        if callable(value):
            value = value()
        return value

    def is_active(self, instance, conditions):
        """
        value is the current value of the switch
        instance is the instance of our type
        """
        for name, field in self.fields.iteritems():
            condition = conditions[self.model.__name__].get(name)
            if condition:
                value = self.get_field_value(instance, name)
                if any(field.is_active(c, value) for c in condition):
                    return True

class RequestSwitch(Switch):
    def can_execute(self, instance):
        return isinstance(instance, HttpRequest)