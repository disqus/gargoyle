"""
gargoyle.models
~~~~~~~~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

import modeldict.dict


class Switch(object):
    """
    A switch encapsulates the concept of an item that is either 'on' or 'off'
    depending on the input.  The swich determines this by checking each of its
    conditions and seeing if it applies to a certain input.  All the switch does
    is ask each of its Conditions if it applies to the provided input.  Normally
    any condition can be true for the Switch to be enabled for a particular
    input, but of ``switch.componded`` is set to True, then **all** of the
    switches conditions need to be true in order to be enabled.

    See the Condition class for more information on what a Condition is and how
    it checks to see if it's satisfied by an input.
    """

    class states:
        DISABLED = 1
        SELECTIVE = 2
        GLOBAL = 3

    def __init__(self, name, state=states.DISABLED, compounded=False):
        self.name = str(name)
        self.state = state
        self.conditions = []
        self.compounded = compounded

    def enabled_for(self, inpt):
        """
        Checks to see if this switch is enabled for the provided input, which is
        an instance of the ``Input`` class.  The switch is enabled if any of its
        conditions are met by the input.
        """
        func = self.__enabled_func()
        return func(cond(inpt) for cond in self.conditions)

    def __enabled_func(self):
        if self.compounded:
            return all
        else:
            return any


class Condition(object):
    """
    A Condition is the configuration of an argument and an operator, and tells
    you if the operator applies to the argument as it exists in the input
    instance passed in.  The previous sentence probably doesn't make any sense,
    so read on!

    The argument defines what this condition is checking.  Perhaps it's the
    request's IP address or the user's name.  Literally, an argumenet is an
    unbound function attached to an available Input class.  For example, for the
    request IP address, you would define an ``ip`` function inside the
    ``RequestInput`` class, and that function object, ``RequestInput.ip`` would
    be the Condition's argument,.

    When the Condition is called, it extracts the same argument from the passed
    in Input.  The extacted ``value`` is then checked against the operator.  An
    operator will tell you if the value meets **its** criteria, like if the
    value is > some number or within a range or percetnage.

    To put it another way, say you wanted a condition to only allow your switch
    to people between 15 and 30 years old.  To make the condition:

        1. You would create a ``UserInput`` class wraps your own User object,
            with a ``age`` method which returns the user's age.
        2. You would then create a new Condition via:
           ``Condition(argument=UserInput.age, operator=Between(15, 30))``.
        3. You then call that condition with an **instance** of a ``UserInput``,
           and it would return True if the age of the user the ``UserInput``
           class wraps is between 15 and 30.
    """

    def __init__(self, argument, operator):
        self.argument = argument
        self.operator = operator
        self.negative = False

    def __call__(self, inpt):
        if not self.__is_same_class_as_argument(inpt):
            return False

        application = self.__apply(inpt)

        if self.negative:
            application = not application

        return application

    def __apply(self, inpt):
        value = self.argument(inpt)
        return self.operator.applies_to(value)

    def __is_same_class_as_argument(self, inpt):
        return inpt.__class__ is self.argument.im_class


class Manager(object):
    """
    The Manager holds all state for Gargoyle.  It knows what Switches have been
    registered, and also what Input objects are currently being applied.  It
    also offers an ``active`` method to ask it if a given switch name is
    active, given its conditions and current inputs.
    """

    def __init__(self, storage):
        self.__switches = storage
        self.inputs = []

    @property
    def switches(self):
        return self.__switches.values()

    def register(self, switch):
        self.__switches[switch.name] = switch

    def input(self, *inputs):
        self.inputs = list(inputs)

    def flush(self):
        self.inputs = []

    def active(self, name):
        try:
            switch = self.__switches[name]
            return any(switch.enabled_for(inpt) for inpt in self.inputs)
        except KeyError:
            raise ValueError("No switch named '%s' registered" % name)
