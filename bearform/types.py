"""Define types to be encoded/decoded."""
import era
from .errors import EncodingError

registered_field_types = []


def register_field_type(field_type):
    """Register a field type."""
    registered_field_types.append(field_type)


def is_type(cls, typ):
    """Return True if the class is of the given type."""
    if not isinstance(cls, type):
        return False
    return issubclass(cls, typ)


class FieldType(object):
    """Abstract class used for defining a field type."""

    @classmethod
    def supported(cls, typ):
        """Return True if the type is supported by the field type."""
        return False

    @classmethod
    def create(cls, typ):
        if isinstance(typ, FieldType):
            return typ
        for field_type in registered_field_types:
            if field_type.supported(typ):
                return field_type(typ)
        return BuiltinType(typ)

    def __init__(self, *args, **kwargs):
        """Initialize the field type."""

    def default(self, value):
        """Process a default value before storing."""
        return value

    def encode(self, cls, name, value):
        """Return the value encoded for transmission to the frontend."""
        return value

    def decode(self, cls, name, value):
        """Return the value decoded from the frontend."""
        return value

    def validate(self, cls, name, value):
        """Raise ValidationError if the field fails to validate."""


class BuiltinType(FieldType):
    """Used for built-in Python types which can be called with a single argument."""

    def __init__(self, builtin):
        """Create a field type using the given builtin type."""
        if is_type(builtin, basestring):
            builtin = unicode
        self.builtin = builtin

    def encode(self, cls, name, value):
        """Return the encoded value."""
        try:
            return self.builtin(value)
        except (TypeError, ValueError):
            msg = "failed to encode value as {}".format(self.builtin.__name__)
            raise EncodingError(msg, cls, name, value, True)

    def decode(self, cls, name, value):
        """Return the decoded value."""
        try:
            return self.builtin(value)
        except (TypeError, ValueError):
            msg = "failed to decode value as {}".format(self.builtin.__name__)
            raise EncodingError(msg, cls, name, value, False)


class DateType(FieldType):
    """Support date values."""

    @classmethod
    def supported(cls, typ):
        """Return True if the type is supported by the field type."""
        return era.is_date_type(typ)

    def encode(self, cls, name, value):
        """Return a date value as a datetime."""
        if era.is_date(value) or era.is_datetime(value):
            return era.tsms(era.truncate(era.to_datetime(value), era.day))
        raise EncodingError(None, cls, name, value, True)

    def decode(self, cls, name, value):
        """Return the date value from the stored datetime."""
        try:
            return era.fromtsms(int(value)).date()
        except (TypeError, ValueError):
            raise EncodingError(None, cls, name, value, False)


class DateTimeType(FieldType):
    """Support datetime values."""

    @classmethod
    def supported(cls, typ):
        """Return True if the type is supported by the field type."""
        return era.is_datetime_type(typ)

    def encode(self, cls, name, value):
        """Convert time and date values into a datetime."""
        try:
            return era.tsms(value)
        except TypeError:
            raise EncodingError(None, cls, name, value, True)

    def decode(self, cls, name, value):
        """Return the datetime value for the stored value."""
        try:
            return era.fromtsms(int(value))
        except (TypeError, ValueError):
            raise EncodingError(None, cls, name, value, False)


class TimeType(FieldType):
    """Support time values."""

    @classmethod
    def supported(cls, typ):
        """Return True if the type is supported by the field type."""
        return era.is_time_type(typ)

    def encode(self, cls, name, value):
        """Convert a datetime into a time."""
        if era.is_time(value) or era.is_datetime(value):
            return era.tsms(era.to_datetime(value).time())
        raise EncodingError(None, cls, name, value, True)

    def decode(self, cls, name, value):
        """Return the time value from the stored datetime."""
        try:
            return era.fromtsms(int(value)).time()
        except (TypeError, ValueError):
            raise EncodingError(None, cls, name, value, False)


class FormType(FieldType):
    """Support subforms."""

    @classmethod
    def supported(cls, typ):
        """Return True if the type is supported by the field type."""
        from .form import Form
        return is_type(typ, Form)

    def __init__(self, form):
        """Create a form type object with the given form class."""
        self.form = form

    def default(self, value):
        """Return the encoded form containing default values."""
        if value is None:
            return self.form().encode()

    def encode(self, cls, name, value):
        """Return the value encoded as a raw form."""
        if isinstance(value, dict):
            return self.form(**value).encode()
        raise EncodingError(None, cls, name, value, True)

    def decode(self, cls, name, value):
        """Return the value decoded as a form object."""
        if isinstance(value, dict):
            return self.form.decode(value).to_dict()
        raise EncodingError(None, cls, name, value, False)

    def validate(self, cls, name, value):
        """Raise ValidationError if the field fails to validate."""
        self.form(**value).validate()


class ListType(FieldType):
    """Support a list of typed values."""

    @classmethod
    def check_type(cls, typ):
        """Return True if obj is a list or tuple."""
        return is_type(typ, list) or is_type(typ, tuple)

    @classmethod
    def check_obj(cls, obj):
        """Return True if obj is a list or tuple."""
        return isinstance(obj, (list, tuple))

    @classmethod
    def supported(cls, typ):
        """Return True if the type is supported by the field type."""
        return cls.check_type(typ) or cls.check_obj(typ)

    def __init__(self, typ):
        """Create a list type using the given type."""
        if typ is None:
            self.typ = None
        else:
            if self.check_type(typ) or self.check_obj(typ) and len(typ) == 0:
                self.typ = None
            elif self.check_obj(typ):
                self.typ = FieldType.create(typ[0])
            else:
                raise TypeError("invalid ListField type {}".format(repr(typ)))

    def encode_element(self, cls, name, value):
        """Return the encoded value for a single list element."""
        return self.typ.encode(cls, name, value)

    def encode(self, cls, name, value):
        """Return the value encoded as a list of encoded values."""
        if self.typ is not None:
            encoded = []
            for item in value:
                encoded.append(self.encode_element(cls, name, item))
            return encoded
        return list(value)

    def decode(self, cls, name, value):
        """Return the value decoded as a list of decoded values."""
        if self.typ is not None:
            decoded = []
            for item in value:
                decoded.append(self.typ.decode(cls, name, item))
            return decoded
        return list(value)


class SetType(FieldType):
    """Support a set of typed values."""

    @classmethod
    def check_type(cls, typ):
        """Return True if type is a set."""
        return is_type(typ, set)

    @classmethod
    def check_obj(cls, obj):
        """Return True if obj is a set."""
        return isinstance(obj, set)

    @classmethod
    def supported(cls, typ):
        """Return True if the type is supported by the field type."""
        return cls.check_type(typ) or cls.check_obj(typ)

    def __init__(self, typ):
        """Create a set type using the given type."""
        if typ is None:
            self.typ = None
        else:
            if self.check_type(typ) or self.check_obj(typ) and len(typ) == 0:
                self.typ = None
            elif self.check_obj(typ):
                self.typ = FieldType.create(list(typ)[0])
            else:
                raise TypeError("invalid ListField type {}".format(repr(typ)))

    def encode(self, cls, name, value):
        """Return the value encoded as a list of encoded values."""
        if self.typ is not None:
            encoded = []
            for item in value:
                encoded.append(self.typ.encode(cls, name, item))
            return encoded
        return list(value)

    def decode(self, cls, name, value):
        """Return the value decoded as a list of decoded values."""
        if self.typ is not None:
            decoded = set()
            for item in value:
                decoded.add(self.typ.decode(cls, name, item))
            return decoded
        return set(value)


class DictType(FieldType):
    """Support a list of type dict values with strings for keys."""

    @classmethod
    def check_type(cls, typ):
        """Return True if obj is a dict."""
        return is_type(typ, dict)

    @classmethod
    def check_obj(cls, obj):
        """Return True if obj is a dict."""
        return isinstance(obj, dict)

    @classmethod
    def supported(cls, typ):
        """Return True if the type is supported by the field type."""
        return cls.check_type(typ) or cls.check_obj(typ)

    def __init__(self, typ):
        """Create s dict type using the given type."""
        if typ is None:
            self.typ = None
        else:
            if self.check_type(typ) or self.check_obj(typ) and len(typ) == 0:
                self.typ = None
            elif self.check_obj(typ):
                self.typ = FieldType.create(typ.values()[0])
            else:
                raise TypeError("invalid DictField type {}".format(repr(typ)))

    def encode(self, cls, name, value):
        """Return the value encoded as a dict of encoded values."""
        if self.typ is not None:
            encoded = {}
            for key, item in value.iteritems():
                encoded[str(key)] = self.typ.encode(cls, name, item)
            return encoded
        return dict(value)

    def decode(self, cls, name, value):
        """Return the value decoded as a list of decoded values."""
        if self.typ is not None:
            decoded = {}
            for key, item in value.iteritems():
                decoded[key] = self.typ.decode(cls, name, item)
            return decoded
        return dict(value)


register_field_type(DateType)
register_field_type(DateTimeType)
register_field_type(TimeType)
register_field_type(FormType)
register_field_type(ListType)
register_field_type(SetType)
register_field_type(DictType)
