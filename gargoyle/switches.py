class ModelSwitch(object):
    """
    needs to provide:
    
    """
    def __init__(self, model, column):
        self.type = model
        self.column = column
    
    def is_active(self, instance, value):
        """
        value is the current value of the switch
        instance is the instance of our type
        """
        col_value = getattr(instance, self.column)
        # if its a character field, exact match
        return col_value == value
        # if its a boolean field, only if its true
        return col_value
        # if its an integer field, only if its in range
        return col_value >= value[0] and col_value <= value[1]
    
class RequestSwitch(object):
    type = WSGIRequest