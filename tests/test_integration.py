import unittest
from nose.tools import *

from gargoyle.operators.comparable import *
from gargoyle.operators.identity import *
from gargoyle.operators.misc import *
from gargoyle.models import Switch, Condition, Manager
from gargoyle.inputs.arguments import Value, Boolean


class User(object):

    def __init__(self, name, age, location='San Francisco', married=False):
        self._name = name
        self._age = age
        self._location = location
        self._married = married

    def name(self):
        return Value(self._name)

    def age(self):
        return Value(self._age)

    def location(self):
        return Value(self._location)

    def married(self):
        return Boolean(self._married)


class TestIntegration(unittest.TestCase):

    def setUp(self):
        self.manager = Manager(storage=dict())

        self.jeff = User('jeff', 21)
        self.steve = User('steve', 10, location="Seattle")
        self.larry = User('bill', 70, location="Yakima", married=True)

        self.age_over_65 = Condition(User.age, MoreThan(65))
        self.age_under_18 = Condition(User.age, LessThan(18))
        self.age_over_21 = Condition(User.age, MoreThan(21))
        self.age_between_13_and_18 = Condition(User.age, Between(13, 18))

        self.in_sf = Condition(User.location, Equals('San Francisco'))
        self.has_location = Condition(User.location, Truthy())

        self.j_name = Condition(User.name, Enum('jeff', 'john', 'josh'))

        self.three_quarters_married = Condition(User.married, Percent(75))
        self.ten_percent = Condition(User.name, Percent(10))

    def switch(self, name, *conditions):
        switch = Switch('can drink')
        [switch.conditions.append(c) for c in conditions]
        return switch

    class inputs(object):

        def __init__(self, test, *inputs):
            self.test = test
            self.manager = self.test.manager
            self.manager.input(*inputs)

        def __enter__(self):
            return self

        def add_switch(name, *conditions):
            switch = Switch('can drink')
            [switch.conditions.append(c) for c in conditions]
            self.manager.register(switch)

        def __exit__(self, type, value, traceback):
            self.manager.flush()

    def test_switches_work_with_conditions(self):
        with self.inputs(self, self.larry) as context:
            context.add_switch('can drink', self.age_over_21)
            ok_(context.manager.active('can drink'))