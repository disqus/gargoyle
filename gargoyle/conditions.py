"""
gargoyle.conditions
~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

# TODO: i18n
# Credit to Haystack for abstraction concepts

import datetime

from django.http import HttpRequest
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.core.validators import ValidationError

from gargoyle.models import EXCLUDE

import itertools


def titlize(s):
    return s.title().replace('_', ' ')


class Field(object):
    default_help_text = None

    def __init__(self, label=None, help_text=None):
        self.label = label
        self.help_text = help_text or self.default_help_text
        self.set_values(None)

    def set_values(self, name):
        self.name = name
        if name and not self.label:
            self.label = titlize(name)

    def is_active(self, condition, value):
        return condition == value

    def validate(self, data):
        value = data.get(self.name)
        if value:
            value = self.clean(value)
            assert isinstance(value, basestring), 'clean methods must return strings'
        return value

    def clean(self, value):
        return value

    def render(self, value):
        return mark_safe('<input type="text" value="%s" name="%s"/>' % (escape(value or ''), escape(self.name)))

    def display(self, value):
        return value
        # return '%s: %s' % (self.label, value) - For Cramer to not to forget how to use his own code


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
        value = filter(None, [data.get(self.name + '[min]'), data.get(self.name + '[max]')]) or None
        return self.clean(value)

    def clean(self, value):
        if value:
            try:
                map(int, value)
            except (TypeError, ValueError):
                raise ValidationError('You must enter valid integer values.')
        return '-'.join(value)

    def render(self, value):
        if not value:
            value = ['', '']
        return mark_safe('<input type="text" value="%s" placeholder="from" name="%s[min]"/> - <input type="text" placeholder="to" value="%s" name="%s[max]"/>' %
                         (escape(value[0]), escape(self.name), escape(value[1]), escape(self.name)))

    def display(self, value):
        value = value.split('-')
        return '%s: %s-%s' % (self.label, value[0], value[1])


class Percent(Range):
    default_help_text = 'Enter two ranges. e.g. 0-50 is lower 50%'

    def is_active(self, condition, value):
        condition = map(int, condition.split('-'))
        mod = value % 100
        return mod >= condition[0] and mod <= condition[1]

    def display(self, value):
        value = value.split('-')
        return '%s: %s%% (%s-%s)' % (self.label, int(value[1]) - int(value[0]), value[0], value[1])

    def clean(self, value):
        value = super(Percent, self).clean(value)
        if value:
            numeric = value.split('-')
            if int(numeric[0]) < 0 or int(numeric[1]) > 100:
                raise ValidationError('You must enter values between 0 and 100.')
            if int(numeric[0]) > int(numeric[1]):
                raise ValidationError('Start value must be less than end value.')
        return value


class String(Field):
    pass


class AbstractDate(Field):
    DATE_FORMAT = "%Y-%m-%d"
    PRETTY_DATE_FORMAT = "%d %b %Y"

    def str_to_date(self, value):
        return datetime.datetime.strptime(value, self.DATE_FORMAT).date()

    def display(self, value):
        date = self.str_to_date(value)
        return "%s: %s" % (self.label, date.strftime(self.PRETTY_DATE_FORMAT))

    def clean(self, value):
        try:
            date = self.str_to_date(value)
        except ValueError, e:
            raise ValidationError("Date must be a valid date in the format YYYY-MM-DD.\n(%s)" % e.message)

        return date.strftime(self.DATE_FORMAT)

    def render(self, value):
        if not value:
            value = datetime.date.today().strftime(self.DATE_FORMAT)

        return mark_safe('<input type="text" value="%s" name="%s"/>' % (escape(value), escape(self.name)))

    def is_active(self, condition, value):
        assert isinstance(value, datetime.date)
        if isinstance(value, datetime.datetime):
            # datetime.datetime cannot be compared to datetime.date with > and < operators
            value = value.date()

        condition_date = self.str_to_date(condition)
        return self.date_is_active(condition_date, value)

    def date_is_active(self, condition_date, value):
        raise NotImplementedError


class BeforeDate(AbstractDate):
    def date_is_active(self, before_this_date, value):
        return value < before_this_date


class OnOrAfterDate(AbstractDate):
    def date_is_active(self, after_this_date, value):
        return value >= after_this_date


class ConditionSetBase(type):
    def __new__(cls, name, bases, attrs):
        attrs['fields'] = {}

        # Inherit any fields from parent(s).
        parents = [b for b in bases if isinstance(b, ConditionSetBase)]

        for p in parents:
            fields = getattr(p, 'fields', None)

            if fields:
                attrs['fields'].update(fields)

        for field_name, obj in attrs.items():
            if isinstance(obj, Field):
                field = attrs.pop(field_name)
                field.set_values(field_name)
                attrs['fields'][field_name] = field

        instance = super(ConditionSetBase, cls).__new__(cls, name, bases, attrs)

        return instance


class ConditionSet(object):
    __metaclass__ = ConditionSetBase

    def __repr__(self):
        return '<%s>' % (self.__class__.__name__,)

    def get_id(self):
        """
        Returns a string representing a unique identifier for this ConditionSet
        instance.
        """
        return '%s.%s' % (self.__module__, self.__class__.__name__)

    def can_execute(self, instance):
        """
        Given an instance, returns a boolean of whether this ConditionSet
        can return a valid condition check.
        """
        return True

    def get_namespace(self):
        """
        Returns a string specifying a unique registration namespace for this ConditionSet
        instance.
        """
        return self.__class__.__name__

    def get_field_value(self, instance, field_name):
        """
        Given an instance, and the name of an attribute, returns the value
        of that attribute on the instance.

        Default behavior will map the ``percent`` attribute to ``id``.
        """
        # XXX: can we come up w/ a better API?
        # Ensure we map ``percent`` to the ``id`` column
        if field_name == 'percent':
            field_name = 'id'
        value = getattr(instance, field_name)
        if callable(value):
            value = value()
        return value

    def has_active_condition(self, conditions, instances):
        """
        Given a list of instances, and the conditions active for
        this switch, returns a boolean reprsenting if any
        conditional is met, including a non-instance default.
        """
        return_value = None
        for instance in itertools.chain(instances, [None]):
            if not self.can_execute(instance):
                continue
            result = self.is_active(instance, conditions)
            if result is False:
                return False
            elif result is True:
                return_value = True
        return return_value

    def is_active(self, instance, conditions):
        """
        Given an instance, and the conditions active for this switch, returns
        a boolean representing if the feature is active.
        """
        return_value = None
        for name, field in self.fields.iteritems():
            field_conditions = conditions.get(self.get_namespace(), {}).get(name)
            if field_conditions:
                value = self.get_field_value(instance, name)
                for status, condition in field_conditions:
                    exclude = status == EXCLUDE
                    if field.is_active(condition, value):
                        if exclude:
                            return False
                        return_value = True
                    else:
                        if exclude:
                            return_value = True
        return return_value

    def get_group_label(self):
        """
        Returns a string representing a human readable version
        of this ConditionSet instance.
        """
        return self.__class__.__name__


class ModelConditionSet(ConditionSet):
    percent = Percent()

    def __init__(self, model):
        self.model = model

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.model.__name__)

    def can_execute(self, instance):
        return isinstance(instance, self.model)

    def get_id(self):
        return '%s.%s(%s)' % (self.__module__, self.__class__.__name__, self.get_namespace())

    def get_namespace(self):
        if hasattr(self.model._meta, 'model_name'):
            model_name = self.model._meta.model_name
        else:
            model_name = self.model._meta.module_name
        return '%s.%s' % (self.model._meta.app_label, model_name)

    def get_group_label(self):
        return self.model._meta.verbose_name.title()


class RequestConditionSet(ConditionSet):
    def get_namespace(self):
        return 'request'

    def can_execute(self, instance):
        return isinstance(instance, HttpRequest)
