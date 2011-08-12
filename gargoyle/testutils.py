from functools import wraps

from gargoyle import gargoyle

def with_switch(gargoyle=gargoyle, **keys):
    """
    Allows temporarily enabling or disabling a switch.
    
    Ideal for testing.
    
    >>> @with_switch(my_switch_name=True)
    >>> def foo():
    >>>     print gargoyle.is_active('my_switch_name')

    >>> @with_switch(gargoyle, my_switch_name=True)
    >>> def foo():
    >>>     print gargoyle.is_active('my_switch_name')
    """
    def _with_switch(func):
        @wraps(func)
        def inner(*args, **kwargs):
            with SwitchContextManager(gargoyle, **keys):
                return func(*args, **kwargs)
        return inner
    return _with_switch

class SwitchContextManager(object):
    """
    While context is active all switches in ``keys``
    are set to ``GLOBAL``. Ideal for testing.
    
    >>> def foo():
    >>>     with SwitchContextManager(my_switch_name=True):
    >>>         print gargoyle.is_active('my_switch_name')


    >>> def foo():
    >>>     with SwitchContextManager(gargoyle, my_switch_name=True):
    >>>         print gargoyle.is_active('my_switch_name')
    
    """
    values = {
        True: gargoyle.GLOBAL,
        False: gargoyle.DISABLED,
    }
    
    def __init__(self, gargoyle=gargoyle, **keys):
        self.gargoyle = gargoyle
        self.keys = keys
        self._state = {}

    def __enter__(self):
        for key, value in self.keys.iteritems():
            self._state[key] = self.gargoyle[key].status
            self.gargoyle[key].status = self.values[value]

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key in self.keys:
            self.gargoyle[key].status = self._state[key]

switches = SwitchContextManager