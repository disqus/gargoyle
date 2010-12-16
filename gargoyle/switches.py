# TODO: i18n

from django.db import models
from django.http import HttpRequest

class BaseSwitch(object):
    def get_type_label(self):
        return self.get_type().__name__
    
    def get_column_label(self):
        return 

class ModelSwitch(BaseSwitch):
    def __init__(self, model, column):
        self.model = model
        self.column = column
    
    def get_type(self):
        return self.model
    
    def get_column_label(self):
        return self.column
    
    def get_group_label(self):
        return self.model._meta.verbose_name
    
    def is_active(self, instance, value):
        """
        value is the current value of the switch
        instance is the instance of our type
        """
        column = self.column
        col_value = getattr(instance, column)

        # support for things like "is_authenticated" being a column
        if callable(col_value):
            col_value = col_value()
        
        # If our column is a ``Field`` we determine its type
        # TODO: abstract to type selectors
        try:
            column = self.model._meta.get_field_by_name(column)[0]
        except models.FieldDoesNotExist:
            pass
        else:
            if isinstance(column, models.CharField):
                # if its a character field, exact match
                return col_value == value
            elif isinstance(column, models.BooleanField):
                # if its a boolean field, only if its true
                return col_value
            elif isinstance(column, (models.IntegerField, models.AutoField)):
                # if its an integer field, only if its in modulus range
                mod = col_value % 100
                return mod >= value[0] and mod <= value[1]
                # XXX: we could also have some kind of user id range support?
                # return col_value >= value[0] and col_value <= value[1]
        # by default we just do exact comparison
        return col_value == column

class RequestSwitch(BaseSwitch):
    def get_type(self):
        return HttpRequest

class IPAddressSwitch(BaseSwitch):
    # TODO:
    pass