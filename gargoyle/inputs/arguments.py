import datetime


class Base(object):

    INVALID_COMPARISON = (False, False)
    VALID_COMPARISON = lambda self, x: (True, x)

    def validate(self, comparison):
        return True

    def __make_value_comparison_func(method):
        def func(self, comparison):
            validation = self.validate(comparison)

            if validation is self.INVALID_COMPARISON:
                # TODO: Make this configurable.  Maybe we want to raise an
                # exception instead of just returning false?
                return False

            _, transformed_comparison = validation

            if hasattr(self, 'value'):
                return getattr(self.value, method)(transformed_comparison)
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


class Date(Base):

    ISO_8601 = "%Y-%m-%d"

    def __init__(self, value):
        self.value = value

    def validate(self, comparison):
        try:
            if not hasattr(comparison, 'isoformat'):
                parsed = datetime.datetime.strptime(comparison, self.ISO_8601)
                comparison = parsed.date()

            return self.VALID_COMPARISON(comparison)
        except ValueError:
            return self.INVALID_COMPARISON
