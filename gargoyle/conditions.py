class Truthy(object):

    label = 'truthy'
    description = 'Applies if the argument is truthy.'

    def applies_to(self, argument):
        return bool(argument)


class Equals(object):

    label = 'equals'
    description = 'Applies of the candidate equals the specified values.'

    def __init__(self, value):
        self.value = value

    def applies_to(self, argument):
        return self.value == argument


class Enum(object):

    label = 'enum'
    description = 'Appies if argument is included in the specified values'

    def __init__(self, *possibilities):
        self.possibilities = possibilities

    def applies_to(self, argument):
        return argument in self.possibilities


class Between(object):

    label = 'range'
    description = 'Applies if argument is between the upper and lower bounds'

    def __init__(self, lower, higher):
        self.lower = lower
        self.higher = higher

    def applies_to(self, argument):
        return argument > self.lower and argument < self.higher


class LessThan(object):

    label = 'before'
    description = 'Applies if argument is before value'

    def __init__(self, upper_limit):
        self.upper_limit = upper_limit

    def applies_to(self, argument):
        return argument < self.upper_limit


class MoreThan(object):

    label = 'more_than'
    description = 'Applies if argument is more than value'

    def __init__(self, lower_limit):
        self.lower_limit = lower_limit

    def applies_to(self, argument):
        return argument > self.lower_limit


class Percent(object):

    label = 'percent'
    description = 'Applies if argument hashes to <= percent value'

    def __init__(self, percentage):
        self.percentage = float(percentage)

    def applies_to(self, argument):
        return hash(argument) % 100 <= self.percentage
