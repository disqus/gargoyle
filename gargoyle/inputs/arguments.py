import random


class Base(object):

    def __proxy_to_value_method(method):
        def func(self, *args, **kwargs):

            if hasattr(self, 'value'):
                return getattr(self.value, method)(*args, **kwargs)
            else:
                raise NotImplementedError

        return func

    __cmp__ = __proxy_to_value_method('__cmp__')
    __hash__ = __proxy_to_value_method('__hash__')
    __nonzero__ = __proxy_to_value_method('__nonzero__')


class Value(Base):

    def __init__(self, value):
        self.value = value


class Boolean(Base):

    def __init__(self, value, hash_value=None):
        self.value = value
        self.hash_value = hash_value or random.getrandbits(128)

    def __hash__(self, *args, **kwargs):
        return hash(self.hash_value)
