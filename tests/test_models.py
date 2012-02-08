import unittest
from nose.tools import *
from gargoyle.models import Switch
import mock


class TestSwitch(unittest.TestCase):

    def test_switch_has_state_constants(self):
        self.assertTrue(Switch.states.DISABLED)
        self.assertTrue(Switch.states.SELECTIVE)
        self.assertTrue(Switch.states.GLOBAL)

    def test_no_switch_is_equal_to_another(self):
        states = (Switch.states.DISABLED, Switch.states.SELECTIVE,
                  Switch.states.GLOBAL)
        eq_(list(states), list(set(states)))

    def test_switch_constructs_with_a_name_attribute(self):
        eq_(Switch('foo').name, 'foo')

    def test_switch_strs_the_name_argument(self):
        eq_(Switch(name=12345).name, '12345')

    def test_switch_state_defaults_to_disabled(self):
        eq_(Switch('foo').state, Switch.states.DISABLED)

    def test_switch_compounded_defaults_to_disabled(self):
        eq_(Switch('foo').compounded, False)

    def test_swtich_can_be_constructed_with_a_state(self):
        switch = Switch(name='foo', state=Switch.states.GLOBAL)
        eq_(switch.state, Switch.states.GLOBAL)

    def test_swtich_can_be_constructed_with_a_compounded_val(self):
        switch = Switch(name='foo', compounded=True)
        eq_(switch.compounded, True)

    def test_conditions_defaults_to_an_empty_list(self):
        eq_(Switch('foo').conditions, [])


class ConditionsTest(object):

    def setUp(self):
        self.switch = Switch('with conditions')
        self.switch.conditions.append(self.pessamistic_condition)
        self.switch.conditions.append(self.pessamistic_condition)

    @property
    def pessamistic_condition(self):
        mck = mock.MagicMock()
        mck.applies_to.return_value = False
        return mck

    def test_condtions_can_be_added_and_removed(self):
        condition = self.pessamistic_condition
        ok_(condition not in self.switch.conditions)

        self.switch.conditions.append(condition)
        ok_(condition in self.switch.conditions)

        self.switch.conditions.remove(condition)
        ok_(condition not in self.switch.conditions)


class DefaultConditionsTest(ConditionsTest, unittest.TestCase):

    def test_enabled_for_is_true_if_any_conditions_are_true(self):
        ok_(self.switch.enabled_for('a val') is False)
        self.switch.conditions[0].applies_to.return_value = True
        ok_(self.switch.enabled_for('a val') is True)

class CompoundedConditionsTest(ConditionsTest, unittest.TestCase):

    def setUp(self):
        super(CompoundedConditionsTest, self).setUp()
        self.switch.compounded = True

    def test_enabled_if_all_conditions_are_true(self):
        ok_(self.switch.enabled_for('a val') is False)
        self.switch.conditions[0].applies_to.return_value = True
        ok_(self.switch.enabled_for('a val') is False)
        self.switch.conditions[1].applies_to.return_value = True
        ok_(self.switch.enabled_for('a val') is True)
