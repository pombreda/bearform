"""Some useful utilities."""


class Struct(object):
    """An object you can put arbitrary attributes on."""

    def __init__(self, **attrs):
        """Initialize the struct with some attributes."""
        for name, value in attrs.iteritems():
            setattr(self, name, value)
