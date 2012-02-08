import unittest
from nose.tools import *
from gargoyle.models import Switch, Manager, Condition
from modeldict.dict import MemoryDict
import mock


switch = Switch('test')


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


class TestCondition(unittest.TestCase):

    class ReflectiveInput(object):

        def foo(self):
            return (42, self)

    def setUp(self):
        self.operator = mock.Mock(name='operator')
        self.operator.applies_to.return_value = True
        self.condition = Condition(self.ReflectiveInput.foo, self.operator)

    def test_returns_false_if_input_is_not_same_class_as_argument_class(self):
        eq_(self.condition(object()), False)

    def test_returns_results_from_calling_operator_with_argument_value(self):
        """
        This test verifies that when a condition is called with an instance of
        an Input as the argument, the vaue that the condition's operator is
        asked if it applies to is calculated by calling the condition's own
        argument function as bound to the instance of the Input originally
        passed in to the condition.

        By using the ReflectiveInput class, we can verify that it was called
        with expected arguments, which are returned in a tuple with an extra
        value (42), and that that tuple is passed to the operator's applied_to
        method.
        """

        input_instance = self.ReflectiveInput()
        self.condition(input_instance)
        self.operator.applies_to.assert_called_once_with((42, input_instance))


class SwitchWithConditions(object):

    def setUp(self):
        self.switch = Switch('with conditions')
        self.switch.conditions.append(self.pessamistic_condition)
        self.switch.conditions.append(self.pessamistic_condition)

    @property
    def pessamistic_condition(self):
        mck = mock.MagicMock()
        mck.return_value = False
        return mck

    def test_condtions_can_be_added_and_removed(self):
        condition = self.pessamistic_condition
        ok_(condition not in self.switch.conditions)

        self.switch.conditions.append(condition)
        ok_(condition in self.switch.conditions)

        self.switch.conditions.remove(condition)
        ok_(condition not in self.switch.conditions)


class DefaultConditionsTest(SwitchWithConditions, unittest.TestCase):

    def test_enabled_for_is_true_if_any_conditions_are_true(self):
        ok_(self.switch.enabled_for('input') is False)
        self.switch.conditions[0].return_value = True
        ok_(self.switch.enabled_for('input') is True)


class CompoundedConditionsTest(SwitchWithConditions, unittest.TestCase):

    def setUp(self):
        super(CompoundedConditionsTest, self).setUp()
        self.switch.compounded = True

    def test_enabled_if_all_conditions_are_true(self):
        ok_(self.switch.enabled_for('input') is False)
        self.switch.conditions[0].return_value = True
        ok_(self.switch.enabled_for('input') is False)
        self.switch.conditions[1].return_value = True
        ok_(self.switch.enabled_for('input') is True)


class ManagerTest(unittest.TestCase):

    def setUp(self):
        self.manager = Manager(storage=MemoryDict())

    def test_input_accepts_variable_input_args(self):
        eq_(self.manager.inputs, [])
        self.manager.input('input1', 'input2')
        eq_(self.manager.inputs, ['input1', 'input2'])

    def test_flush_clears_all_inputs(self):
        self.manager.input('input1', 'input2')
        ok_(len(self.manager.inputs) is 2)
        self.manager.flush()
        ok_(len(self.manager.inputs) is 0)

    def test_register_adds_switch_to_storge_keyed_by_its_name(self):
        mockstorage = mock.MagicMock(MemoryDict())
        Manager(storage=mockstorage).register(switch)
        mockstorage.__setitem__.assert_called_once_with(switch.name, switch)

    def test_switches_list_registed_switches(self):
        eq_(self.manager.switches, [])
        self.manager.register(switch)
        eq_(self.manager.switches, [switch])

    def test_active_raises_exception_if_no_switch_found_with_name(self):
        assert_raises(ValueError, self.manager.active, 'junk')


class ManagerActiveTest(unittest.TestCase):

    def build_and_register_switch(self, name, enabled_for=False):
        switch = Switch(name)
        switch.enabled_for = mock.Mock(return_value=enabled_for)
        self.manager.register(switch)
        return switch

    def setUp(self):
        self.manager = Manager(storage=MemoryDict())
        self.manager.input('input 1', 'input 2')

    def test_returns_false_if_named_switch_is_enabled_for_any_input(self):
        self.build_and_register_switch('disabled', enabled_for=False)
        eq_(self.manager.active('disabled'), False)

        self.build_and_register_switch('enabled', enabled_for=True)
        eq_(self.manager.active('disabled'), False)
