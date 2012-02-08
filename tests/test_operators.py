import unittest
from nose.tools import *
from gargoyle.operators import *


class BaseCondition(object):

    def test_has_label(self):
        ok_(self.condition.label)

    def test_has_description(self):
        ok_(self.condition.description)

    def test_has_applies_to_method(self):
        ok_(self.condition.applies_to)


class TestTruthyCondition(BaseCondition, unittest.TestCase):

    @property
    def condition(self):
        return Truthy()

    def test_applies_to_if_argument_is_truthy(self):
        ok_(self.condition.applies_to(True))
        ok_(self.condition.applies_to("hello"))
        ok_(self.condition.applies_to(False) is False)
        ok_(self.condition.applies_to("") is False)


class TestEqualsCondition(BaseCondition, unittest.TestCase):

    @property
    def condition(self):
        return Equals(value='Fred')

    def test_applies_to_if_argument_is_equal_to_value(self):
        ok_(self.condition.applies_to('Fred'))
        ok_(self.condition.applies_to('Steve') is False)
        ok_(self.condition.applies_to('') is False)
        ok_(self.condition.applies_to(True) is False)

    @raises(TypeError)
    def test_raises_error_if_not_provided_value(self):
        Equals()


class TestEnumCondition(BaseCondition, unittest.TestCase):

    @property
    def condition(self):
        return Enum(False, 2.0, '3')

    def test_applies_to_if_argument_in_enum(self):
        ok_(self.condition.applies_to(False))
        ok_(self.condition.applies_to(2.0))
        ok_(self.condition.applies_to(9) is False)
        ok_(self.condition.applies_to("1") is False)
        ok_(self.condition.applies_to(True) is False)


class TestBetweenCondition(BaseCondition, unittest.TestCase):

    @property
    def condition(self, lower=1, higher=100):
        return Between(lower, higher)

    def test_applies_to_if_between_lower_and_upper_bound(self):
        ok_(self.condition.applies_to(0) is False)
        ok_(self.condition.applies_to(1) is False)
        ok_(self.condition.applies_to(2))
        ok_(self.condition.applies_to(99))
        ok_(self.condition.applies_to(100) is False)
        ok_(self.condition.applies_to('steve') is False)

    def test_applies_to_works_with_any_comparable(self):
        animals = Between('cobra', 'orangatang')
        ok_(animals.applies_to('dog'))
        ok_(animals.applies_to('elephant'))
        ok_(animals.applies_to('llama'))
        ok_(animals.applies_to('aardvark') is False)
        ok_(animals.applies_to('whale') is False)
        ok_(animals.applies_to('zebra') is False)


class TestLessThanCondition(BaseCondition, unittest.TestCase):

    @property
    def condition(self, upper=500):
        return LessThan(upper)

    def test_applies_to_if_value_less_than_argument(self):
        ok_(self.condition.applies_to(float("-inf")))
        ok_(self.condition.applies_to(-50000))
        ok_(self.condition.applies_to(-1))
        ok_(self.condition.applies_to(0))
        ok_(self.condition.applies_to(499))
        ok_(self.condition.applies_to(500) is False)
        ok_(self.condition.applies_to(10000) is False)
        ok_(self.condition.applies_to(float("inf")) is False)

    def test_works_with_any_comparable(self):
        ok_(LessThan('giraffe').applies_to('aardvark'))
        ok_(LessThan('giraffe').applies_to('zebra') is False)
        ok_(LessThan(56.7).applies_to(56))
        ok_(LessThan(56.7).applies_to(56.0))
        ok_(LessThan(56.7).applies_to(57.0) is False)
        ok_(LessThan(56.7).applies_to(56.71) is False)

class TestMoreThanCondition(BaseCondition, unittest.TestCase):

    @property
    def condition(self, lower=10):
        return MoreThan(lower)

    def test_applies_to_if_value_more_than_argument(self):
        ok_(self.condition.applies_to(float("inf")))
        ok_(self.condition.applies_to(10000))
        ok_(self.condition.applies_to(11))
        ok_(self.condition.applies_to(10) is False)
        ok_(self.condition.applies_to(0) is False)
        ok_(self.condition.applies_to(-100) is False)
        ok_(self.condition.applies_to(float('-inf')) is False)

    def test_works_with_any_comparable(self):
        ok_(MoreThan('giraffe').applies_to('zebra'))
        ok_(MoreThan('giraffe').applies_to('aardvark') is False)
        ok_(MoreThan(56.7).applies_to(57))
        ok_(MoreThan(56.7).applies_to(57.0))
        ok_(MoreThan(56.7).applies_to(56.0) is False)
        ok_(MoreThan(56.7).applies_to(56.71))


class TestPercentCondition(BaseCondition, unittest.TestCase):

    @property
    def condition(self):
        return Percent(50)

    def test_applies_to_percentage_passed_in(self):
        runs = map(self.condition.applies_to, range(1000))
        successful_runs = filter(bool, runs)
        self.assertAlmostEqual(len(successful_runs), 500, delta=50)