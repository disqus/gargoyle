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
    depending on the context.  A Switch object **itself** is not on or off, but
    rather it can be asked if it is on/off when applied to a context.
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
        func = self.__enabled_func()
        return func(cond(inpt) for cond in self.conditions)

    def __enabled_func(self):
        if self.compounded:
            return all
        else:
            return any


class Condition(object):

    def __init__(self, argument, operator):
        self.argument = argument
        self.operator = operator

    def __call__(self, inpt):
        if inpt.__class__ is not self.argument.im_class:
            return False

        value = self.argument(inpt)
        return self.operator.applies_to(value)


class Manager(object):

    def __init__(self, storage=modeldict.dict.RedisDict):
        self.__switches = storage
        self.inputs = []

    @property
    def switches(self):
        return self.__switches.values()

    def arguments_for(self, condition):
        for i in self.inputs:
            for arg in i.arguments:
                yield argument

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