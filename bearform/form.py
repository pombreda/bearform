"""Form classes."""
from .errors import ValidationError
from .meta import FormBuilder
from .types import FormType, ListType, SetType, DictType
from .utils import Struct


class Form(object):
    """A form."""
    __metaclass__ = FormBuilder

    @classmethod
    def from_obj(cls, obj):
        """
        Return a form object containing the values extracted from attributes on the provided
        object. No decoding or validation is performed. This has the same effect as passing the
        values as kwargs to `__init__`. Missing attributes are skipped.
        """
        def obj_to_dict(form, obj):
            values = {}
            for name, field in form._meta.fields.iteritems():
                if hasattr(obj, name):
                    value = getattr(obj, name)
                    if value is not None:
                        if isinstance(field.typ, FormType):
                            value = obj_to_dict(field.typ.form, value)
                        if (isinstance(field.typ, (ListType, SetType)) and
                                isinstance(field.typ.typ, FormType)):
                            value = [obj_to_dict(field.typ.typ.form, v) for v in value]
                        if (isinstance(field.typ, DictType) and
                                isinstance(field.typ.typ, FormType)):
                            value = {k: obj_to_dict(field.typ.typ.form, v)
                                     for k, v in value.iteritems()}
                    values[name] = value
            return values

        values = obj_to_dict(cls, obj)
        return cls(**values)

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

    def encode(self, missing=False):
        """
        Return the form data encoded as a dictionary ready for serialization. Data is not validated
        during this method. If missing is True then fields set to `None` will be included.
        """
        encoded = {}
        for name, field in self._meta.fields.iteritems():
            value = self._attrs.get(name)
            if value is not None:
                value = field.encode(self.__class__, name, value)
            if value is not None or missing:
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
