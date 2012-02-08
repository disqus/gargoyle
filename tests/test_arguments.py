import unittest
import datetime
from mock import MagicMock, Mock
from nose.tools import *
from gargoyle.inputs.arguments import *


class BaseArgument(object):

    @property
    def interface_functions(self):
        return ['__lt__', '__le__', '__eq__', '__ne__', '__gt__', '__ge__',
                     '__cmp__', '__hash__']

    @property
    def interface_methods(self):
        return [getattr(self.argument, f) for f in self.interface_functions]

    def test_implements_comparison_methods(self):
        map(ok_, self.interface_methods)


class DelegateToValue(object):

    def test_delegates_all_interface_function_to_the_value_passed_in(self):
        value_passed_in = MagicMock()
        value_passed_in.__cmp__ = Mock()
        argument = Date(value_passed_in)

        for function in self.interface_functions:
            value_function = getattr(value_passed_in, function)
            getattr(argument, function)(self.valid_comparison_value)
            value_function.assert_called_once_with(self.valid_comparison_value)


class TestDateArgument(BaseArgument, DelegateToValue, unittest.TestCase):

    def setUp(self):
        self.argument = Date(self.valid_comparison_value)

    @property
    def valid_comparison_value(self):
        return datetime.date.today()

    def test_returns_false_unless_date_is_in_correct_format(self):
        for method in self.interface_methods:
            eq_(method('junk'), False)
            eq_(method('January 1st, 2020'), False)