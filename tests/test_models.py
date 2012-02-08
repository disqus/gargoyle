import unittest
from nose.tools import *
from gargoyle.models import Switch, Manager
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

    input1 = object()
    input2 = object()

    def setUp(self):
        self.manager = Manager(storage=MemoryDict())
        self.manager.input(self.input1, self.input2)

    @mock.patch('input1.arguments')
    def test_active_returns_value_of_the_switches_enabled_for(self):
        switch.enabled_for = mock.Mock(return_value=False)
        self.manager.register(switch)
        eq_(self.manager.active(switch.name), False)
