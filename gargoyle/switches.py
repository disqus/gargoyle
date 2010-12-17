# TODO: i18n
# Credit to Haystack for abstraction concepts

from django.http import HttpRequest
from django.utils.html import escape
from django.utils.safestring import mark_safe

def titlize(s):
    return s.title().replace('_', ' ')

class ValidationError(Exception): pass

class Field(object):
    default_help_text = None
    
    def __init__(self, label=None, help_text=None):
        self.label = label
        self.help_text = help_text or self.default_help_text
        self.set_name(None)
    
    def set_name(self, name):
        self.name = name
        if name and not self.label:
            self.label = titlize(name)
    
    def is_active(self, condition, value):
        return condition == value

    def validate(self, data):
        value = data.get(self.name)
        return self.clean(value)

    def clean(self, value):
        return value

    def render(self, value):
        return mark_safe('<input type="text" value="%s" name="%s"/>' % (escape(value or ''), escape(self.name)))

    def display(self, value):
        return '%s: %s' % (self.label, value)

class Boolean(Field):
    def is_active(self, condition, value):
        return bool(value)
    
    def render(self, value):
        return mark_safe('<input type="hidden" value="1" name="%s"/>' % (escape(self.name),))

    def display(self, value):
        return self.label

class Choice(Field):
    def __init__(self, choices, **kwargs):
        self.choices = choices
        super(Choice, self).__init__(**kwargs)

    def is_active(self, condition, value):
        return value in self.choices
    
    def clean(self, value):
        if value not in self.choices:
            raise ValidationError
        return value

class Range(Field):
    def is_active(self, condition, value):
        return value >= condition[0] and value <= condition[1]

    def validate(self, data):
        value = [data.get(self.name + '[min]'), data.get(self.name + '[max]')]
        return self.clean(value)

    def render(self, value):
        if not value:
            value = ['', '']
        return mark_safe('<input type="text" value="%s" placeholder="from" name="%s[min]"/> - <input type="text" placeholder="to"  value="%s" name="%s[max]"/>' % \
                         (escape(value[0]), escape(self.name), escape(value[1]), escape(self.name)))

    def display(self, value):
        return '%s: %s-%s' % (self.label, value[0], value[1])

class Percent(Range):
    default_help_text = 'Enter two ranges. e.g. 0-50 is lower 50%'
    
    def is_active(self, condition, value):
        mod = value % 100
        return mod >= condition[0] and mod <= condition[1]

    def display(self, value):
        return '%s: %s%% (%s-%s)' % (self.label, value[1]-value[0], value[0], value[1])

class String(Field):
    pass

class SwitchBase(type):
    def __new__(cls, name, bases, attrs):
        attrs['fields'] = {}
        
        # Inherit any fields from parent(s).
        parents = [b for b in bases if isinstance(b, SwitchBase)]
        
        for p in parents:
            fields = getattr(p, 'fields', None)
            
            if fields:
                attrs['fields'].update(fields)
            
        for field_name, obj in attrs.items():
            if isinstance(obj, Field):
                field = attrs.pop(field_name)
                field.set_name(field_name)
                attrs['fields'][field_name] = field
        
        return super(SwitchBase, cls).__new__(cls, name, bases, attrs)

class Switch(object):
    __metaclass__ = SwitchBase

    def __repr__(self):
        return '<%s>' % (self.__class__.__name__,)

    def can_execute(self, instance):
        return True

    def get_namespace(self):
        return self.__class__.__name__

    def get_field_value(self, instance, field_name):
        # XXX: can we come up w/ a better API?
        # Ensure we map ``percent`` to the ``id`` column
        if field_name == 'percent':
            field_name = 'id'
        value = getattr(instance, field_name)
        if callable(value):
            value = value()
        return value

    def is_active(self, instance, conditions):
        """
        conditions are the current value of the switch
        instance is the instance of our type
        """
        for name, field in self.fields.iteritems():
            condition = conditions.get(self.get_namespace(), {}).get(name)
            if condition:
                value = self.get_field_value(instance, name)
                if any(field.is_active(c, value) for c in condition):
                    return True

class ModelSwitch(Switch):
    def __init__(self, model):
        self.model = model

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.model.__name__)

    def can_execute(self, instance):
        return isinstance(instance, self.model)
    
    def get_namespace(self):
        return '%s.%s' % (self.model._meta.app_label, self.model._meta.module_name)
    
    def get_type(self):
        return self.model
    
    def get_group_label(self):
        return self.model._meta.verbose_name.title()

class RequestSwitch(Switch):
    def get_namespace(self):
        return 'request'
    
    def can_execute(self, instance):
        return isinstance(instance, HttpRequest)