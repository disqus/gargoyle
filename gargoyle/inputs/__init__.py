class Base(object):
    """
    An input is an object which understands the business objects in your system
    (users, requests, etc) and knows how to validate and transform them into
    arguments for operators.  For instance, you may have a User object that
    has properties like ``is_admin``, ``date_joined``, etc.  You would create
    an UserInput object, which wraps a User instance, and provides API methods,
    which return Argument objects.

    By default, any callable public attribute of a decendant of Base is
    considered an argument and returned from the ``arguments`` property.
    Subclasses that which to change that behavior can implement their own
    implementation of ``arguments``.
    """

    @property
    def arguments(self):
        return [getattr(self.__class__, attr) for attr
                in self.callable_attributes()]

    def callable_attributes(self):
        return (
            key for key, value in self.__class__.__dict__.items()
            if callable(value) and not key.startswith('_')
        )

    @classmethod
    def supports(klass, argument, operator):
        """
        Lets input classes return if its argument suports the operator.
        """

        if not callable(argument) or argument.im_class is not klass:
            raise ValueError("'%s' not valid Input Argument" % argument)

        return True
