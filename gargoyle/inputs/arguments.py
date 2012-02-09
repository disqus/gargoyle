class Base(object):

    def __proxy_to_value_method(method):
        def func(self, *args, **kwargs):

            if hasattr(self, 'value'):
                return getattr(self.value, method)(*args, **kwargs)
            else:
                raise NotImplementedError

        return func

    __lt__ = __proxy_to_value_method('__lt__')
    __le__ = __proxy_to_value_method('__le__')
    __eq__ = __proxy_to_value_method('__eq__')
    __ne__ = __proxy_to_value_method('__ne__')
    __gt__ = __proxy_to_value_method('__gt__')
    __ge__ = __proxy_to_value_method('__ge__')
    __cmp__ = __proxy_to_value_method('__cmp__')
    __hash__ = __proxy_to_value_method('__hash__')
    __nonzero__ = __proxy_to_value_method('__nonzero__')


class Value(Base):

    def __init__(self, value):
        self.value = value
