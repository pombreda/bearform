"""Meta functionality used for form creation."""
from .field import Field


class FormMeta(object):
    """Metadata container for Form clsses."""

    def __init__(self, cls, attrs, meta):
        """Initialize new form class metadata."""
        self.cls = cls
        self.fields = {}
        self.options = {}
        self.bind_init()

        if attrs:
            for name, attr in attrs.items():
                if isinstance(attr, Field):
                    self.fields[name] = attr

        if meta:
            self.options.update(vars(meta))

        self.bind_fields()

    def bind_init(meta):
        """Bind init hook to the form class."""
        parent = meta.cls.__init__
        # prevent recursive decoration
        if hasattr(parent, 'parent'):
            parent = parent.parent

        def __init__(self, *args, **kwargs):
            self._attrs = meta.defaults.copy()
            return parent(self, *args, **kwargs)

        __init__.name = parent.__name__
        __init__.hook = True
        __init__.parent = parent
        meta.cls.__init__ = __init__

    def bind_fields(self):
        """Bind fields to the form class."""
        defaults = {}
        for name, field in self.fields.items():
            setattr(self.cls, name, field(self.cls, name))
            default = field.default
            if default is not None:
                default = field.encode(self.cls, name, field.default)
            defaults[name] = default

        self.defaults = defaults


class FormBuilder(type):
    """Metaclass for building form classes."""

    def __new__(meta, name, bases, attrs):
        """Create and attach metadata to the form."""
        Meta = attrs.pop('Meta', {})
        cls = type.__new__(meta, name, bases, attrs)
        cls._meta = FormMeta(cls, attrs, Meta)
        return cls
