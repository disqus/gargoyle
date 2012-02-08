class Base(object):
    """
    An input is an object which understands the business objects in your system
    (users, requests, etc) and knows how to validate and transform them into
    arguments for conditions.  For instance, you may have a User object that
    has properties like ``.is_admin``, ``date_joined``, etc.  You would create
    an UserInput object, which wraps a User instance, and provides the right API
    methods to create Arguments for Conditions.

    An Input also knows how to transform the value the argument is compared to
    inside the condition.  For example, if your ``UserInput`` had an argument
    called ``join_date`` and was being used in a ``LessThan`` conditional, the
    argument would be expected to implement the ``__lt__`` method in order to be
    accurately compared insude the ``LessThan`` conditional.
    """
    pass
