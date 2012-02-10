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

    def test_provides_supports_method(self):
        ok_(DumbInput.supports)

    def test_supports_returns_true_for_everything_by_default(self):
        instance = DumbInput()
        ok_(DumbInput.supports(instance.arg1, 'operator'))
        ok_(DumbInput.supports(instance.arg2, 'operator'))

    def test_supports_raises_exception_if_passed_non_input(self):
        assert_raises_regexp(ValueError, 'not valid Input Argument',
                             DumbInput.supports, 'junk', 'operator')
