class Percent(object):

    label = 'percent'
    description = 'Applies if argument hashes to <= percent value'

    def __init__(self, percentage):
        self.percentage = float(percentage)

    def applies_to(self, argument):
        if not argument:
            return False
        else:
            return hash(argument) % 100 <= self.percentage
