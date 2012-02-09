class Truthy(object):

    label = 'truthy'
    description = 'Applies if the argument is truthy.'

    def applies_to(self, argument):
        return bool(argument)


class Enum(object):

    label = 'enum'
    description = 'Appies if argument is included in the specified values'

    def __init__(self, *possibilities):
        self.possibilities = possibilities

    def applies_to(self, argument):
        return argument in self.possibilities
