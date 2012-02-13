import unittest
from nose.tools import *

from gargoyle.operators.comparable import *
from gargoyle.operators.identity import *
from gargoyle.operators.misc import *
from gargoyle.models import Switch, Condition, Manager
from gargoyle.inputs.arguments import Value, Boolean, String


class User(object):

    def __init__(self, name, age, location='San Francisco', married=False):
        self._name = name
        self._age = age
        self._location = location
        self._married = married

    def name(self):
        return String(self._name)

    def age(self):
        return Value(self._age)

    def location(self):
        return String(self._location)

    def married(self):
        return Boolean(self._married)


class TestIntegration(unittest.TestCase):

    def setUp(self):
        self.manager = Manager(storage=dict())

        self.jeff = User('jeff', 21)
        self.frank = User('frank', 10, location="Seattle")
        self.larry = User('bill', 70, location="Yakima", married=True)

        self.age_over_65 = Condition(User.age, MoreThan(65))
        self.age_under_18 = Condition(User.age, LessThan(18))
        self.age_not_under_18 = Condition(User.age, LessThan(18))
        self.age_not_under_18.negative = True  # TODO Make negative part of constructor
        self.age_over_20 = Condition(User.age, MoreThan(20))
        self.age_between_13_and_18 = Condition(User.age, Between(13, 18))

        self.in_sf = Condition(User.location, Equals('San Francisco'))
        self.has_location = Condition(User.location, Truthy())

        self.j_named = Condition(User.name, Enum('jeff', 'john', 'josh'))

        self.three_quarters_married = Condition(User.married, Percent(75))
        self.ten_percent = Condition(User.name, Percent(10))

        self.add_switch('can drink', condition=self.age_over_20)
        self.add_switch('retired', condition=self.age_over_65)
        self.add_switch('can vote', condition=self.age_not_under_18)
        self.add_switch('teenager', condition=self.age_between_13_and_18)
        self.add_switch('SF resident', condition=self.in_sf)
        self.add_switch('teen or in SF', self.age_between_13_and_18, self.in_sf)
        self.add_switch('teen and in SF', self.age_between_13_and_18,
                        self.has_location, compounded=True)
        self.add_switch('10 percent', self.ten_percent)


    def add_switch(self, name, condition=None, *conditions, **kwargs):
        switch = Switch(name, compounded=kwargs.get('compounded', False))
        conditions = list(conditions)

        if condition:
            conditions.append(condition)

        [switch.conditions.append(c) for c in conditions]
        self.manager.register(switch)

    class inputs(object):

        def __init__(self, manager, *inputs):
            self.manager = manager
            self.manager.input(*inputs)

        def __enter__(self):
            return self

        def active(self, name):
            return self.manager.active(name)

        def __exit__(self, type, value, traceback):
            self.manager.flush()

    def test_basic_switches_work_with_conditions(self):

        with self.inputs(self.manager, self.larry) as manager:
            ok_(manager.active('can drink') is True)
            ok_(manager.active('can vote') is True)
            ok_(manager.active('SF resident') is False)
            ok_(manager.active('retired') is True)
            ok_(manager.active('10 percent') is False)

        with self.inputs(self.manager, self.jeff) as manager:
            ok_(manager.active('can drink') is True)
            ok_(manager.active('can vote') is True)
            ok_(manager.active('SF resident') is True)
            ok_(manager.active('teenager') is False)
            ok_(manager.active('teen or in SF') is True)
            ok_(manager.active('teen and in SF') is False)
            ok_(manager.active('10 percent') is False)

        with self.inputs(self.manager, self.frank) as manager:
            ok_(manager.active('can drink') is False)
            ok_(manager.active('can vote') is False)
            ok_(manager.active('teenager') is False)
            ok_(manager.active('10 percent') is True)

    def test_switches_with_multiple_inputs(self):

        with self.inputs(self.manager, self.larry, self.jeff) as manager:
            ok_(manager.active('can drink') is True)
            ok_(manager.active('SF resident') is True)
            ok_(manager.active('teenager') is False)
            ok_(manager.active('10 percent') is False)

        with self.inputs(self.manager, self.frank, self.jeff) as manager:
            ok_(manager.active('can drink') is True)
            ok_(manager.active('SF resident') is True)
            ok_(manager.active('teenager') is False)
            ok_(manager.active('10 percent') is True)