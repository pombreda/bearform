"""Form classes."""
from .errors import ValidationError
from .meta import FormBuilder
from .types import FormType
from .utils import Struct


class Form(object):
    """A form."""
    __metaclass__ = FormBuilder

    @classmethod
    def decode(cls, raw, extra=None, require=True, validate=True):
        """
        Return a form object containing the raw form data. By default fields present in raw that
        are not defined on the form will cause a ValidationError. If extra is True then all extra
        fields are ignored. If extra is a list then extra fields in that list will be ignored.
        Fields not in the list will still cause a ValidationError. By default values missing in raw
        whose field has require=True will raise a ValidationError. If the require parameter is set
        to False then these values will be replaced with their defaults. Values in raw set to None
        are considered to be missing. If the validate parameter is False then field validation will
        be skipped.
        """
        raw = raw.copy()
        attrs = {}
        for name, field in cls._meta.fields.iteritems():
            value = raw.pop(name, None)
            if value is None and require and field.require:
                msg = "{} data is missing required fields: {}".format(cls.__name__, name)
                raise ValidationError(msg)
            if value is not None:
                attrs[name] = field.decode(cls, name, value)
        if len(raw) > 0 and extra is not True:
            invalid = set(raw.keys()) - (extra and set(extra) or set())
            if invalid:
                invalid = ', '.join(sorted(invalid))
                msg = "{} data has extra fields: {}".format(cls.__name__, invalid)
                raise ValidationError(msg)
        form = cls()
        form._attrs.update(attrs)
        if validate:
            form.validate()
        return form

    def __init__(self, *args, **kwargs):
        """Initialize a form object."""
        for name, value in kwargs.iteritems():
            setattr(self, name, value)

    def encode(self):
        """
        Return the form data encoded as a dictionary ready for serialization. Data is not validated
        during this method.
        """
        encoded = {}
        for name, field in self._meta.fields.iteritems():
            value = self._attrs.get(name)
            if value is not None:
                value = field.encode(self.__class__, name, value)
            encoded[name] = value
        return encoded

    def validate(self):
        """Validate the decoded form data. Raise ValidationError on failure."""
        for name, field in self._meta.fields.iteritems():
            value = self._attrs.get(name)
            if value is None and field.require is True:
                msg = "{} data is missing required fields: {}"
                raise ValidationError(msg.format(self.__class__.__name__, name))
            field.validate(self.__class__, name, value)

    def to_dict(self):
        """Return the decoded form data as a dictionary."""
        def copy(value):
            if isinstance(value, dict):
                value = {k: copy(v) for k, v in value.iteritems()}
            return value
        return copy(self._attrs)

    def to_obj(self, obj=None):
        """
        Return the decoded form data as an object. If the obj parameter is provided then it will be
        loaded with the data. Otherwise a new object is created to return.
        """
        if obj is None:
            obj = Struct()
        for name, field in self._meta.fields.iteritems():
            value = self._attrs.get(name)
            if isinstance(field.typ, FormType):
                obj_attr = getattr(obj, name, None)
                subform = field.typ.form(**value)
                value = subform.to_obj(obj_attr)
            setattr(obj, name, value)
        return obj
