"""
gargoyle.testutils
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from functools import wraps

from gargoyle import gargoyle


class SwitchContextManager(object):
    """
    Allows temporarily enabling or disabling a switch.

    Ideal for testing.

    >>> @switches(my_switch_name=True)
    >>> def foo():
    >>>     print gargoyle.is_active('my_switch_name')

    >>> def foo():
    >>>     with switches(my_switch_name=True):
    >>>         print gargoyle.is_active('my_switch_name')

    You may also optionally pass an instance of ``SwitchManager``
    as the first argument.

    >>> def foo():
    >>>     with switches(gargoyle, my_switch_name=True):
    >>>         print gargoyle.is_active('my_switch_name')
    """
    def __init__(self, gargoyle=gargoyle, **keys):
        self.gargoyle = gargoyle
        self.keys = keys
        self._state = {}
        self._values = {
            True: gargoyle.GLOBAL,
            False: gargoyle.DISABLED,
        }

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return inner

    def __enter__(self):
        for key, value in self.keys.iteritems():
            self._state[key] = self.gargoyle[key].status
            self.gargoyle[key].status = self._values[value]

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key in self.keys:
            self.gargoyle[key].status = self._state[key]

switches = SwitchContextManager
