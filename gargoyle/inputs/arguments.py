class Base(object):

    def __make_value_comparison_func(method):
        def func(self, comparison):

            if hasattr(self, 'value'):
                return getattr(self.value, method)(comparison)
            else:
                raise NotImplementedError

        return func

    __lt__ = __make_value_comparison_func('__lt__')
    __le__ = __make_value_comparison_func('__le__')
    __eq__ = __make_value_comparison_func('__eq__')
    __ne__ = __make_value_comparison_func('__ne__')
    __gt__ = __make_value_comparison_func('__gt__')
    __ge__ = __make_value_comparison_func('__ge__')
    __cmp__ = __make_value_comparison_func('__cmp__')
    __hash__ = __make_value_comparison_func('__hash__')


class Value(Base):

    def __init__(self, value):
        self.value = value
