"""Field objects."""
from .types import FieldType


class Field(object):
    """A field object defines how a field is serialized and validated."""

    def __init__(self, typ, require=True, default=None, validators=None, strict=True):
        """
        Initialize a new field. typ is the type of the field and may be a FieldType or a built-in
        Python type. require is a boolean that indicates whether or not the field is required.
        default is the default value to be stored if the field's value is None. strict determines
        whether or not type conversion and validation should occur during storage and retrieval of
        the field.
        """
        self.typ = FieldType.create(typ)
        self.require = require
        self.default = self.typ.default(default)
        self.strict = strict
        self.validators = [self.typ.validate]
        if validators:
            self.validators.extend(validators)

    def getter(self, obj, name):
        """Return a form attribute as this field."""
        try:
            return obj._attrs[name]
        except KeyError:
            msg = "'{}' object has no attribute '{}'".format(obj.__class__.__name__, name)
            raise AttributeError(msg)

    def setter(self, obj, name, value):
        """Set a form attribute as this field."""
        obj._attrs[name] = value

    def __call__(field, doc, name):
        """Return the form property used to access the field."""
        @property
        def prop(self):
            return field.getter(self, name)

        @prop.setter
        def prop(self, value):
            return field.setter(self, name, value)

        return prop

    def ensure(self, func):
        """
        Ensure the field value passes the provided validation function. The validation function
        takes three arguments: the document, the field name, and the field value. It raises
        ValidationError if validation failes.
        """
        self.validators.append(func)

    def encode(self, cls, name, value):
        """Return the value encoded for the frontend."""
        if self.strict:
            value = self.typ.encode(cls, name, value)
        return value

    def decode(self, cls, name, value):
        """Return the value decoded from the frontend."""
        if self.strict:
            value = self.typ.decode(cls, name, value)
        return value

    def validate(self, cls, name, value):
        """Validate the decoded field value. Raise ValidationError on failure."""
        if self.strict:
            for validator in self.validators:
                validator(cls, name, value)
