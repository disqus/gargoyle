import unittest
from nose.tools import *
from gargoyle.inputs import Base as BaseInput
from gargoyle.inputs.arguments import Value as ValueArgument


class DumbInput(BaseInput):

    foo = 'not part of arguments'

    def arg1(self):
        return ValueArgument('happy')

    def arg2(self):
        return ValueArgument('go lucky')

    def _helper(self):
        pass

    def __other_helper(self):
        pass


class TestBaseInput(unittest.TestCase):

    def test_provides_a_arguments_method(self):
        ok_(DumbInput.arguments)

    def test_arguments_returns_all_public_callable_attributes(self):
        expected = [DumbInput.arg1, DumbInput.arg2]
        self.assertItemsEqual(DumbInput().arguments, expected)
