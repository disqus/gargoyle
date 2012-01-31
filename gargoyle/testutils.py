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
        self.is_active_func = gargoyle.is_active
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
        self.patch()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unpatch()

    def patch(self):
        def is_active(gargoyle):
            is_active_func = gargoyle.is_active

            def wrapped(key, *args, **kwargs):
                if key in self.keys:
                    return self.keys[key]
                return is_active_func(key, *args, **kwargs)
            return wrapped

        self.gargoyle.is_active = is_active(self.gargoyle)

    def unpatch(self):
        self.gargoyle.is_active = self.is_active_func

switches = SwitchContextManager
