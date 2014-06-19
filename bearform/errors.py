"""Framework errors."""


class Error(Exception):
    """Base error type."""


class FormError(Error):  # pragma: no cover
    """Base class for all form related errors."""
    message = "form error"

    def __init__(self, message=None, form=None, field=None, value=None):
        """Format a form or field error message."""
        message = message or self.message
        if form:
            if isinstance(form, type):
                form = form.__name__
            elif isinstance(form, object):
                form = form.__class__.__name__
            if field:
                message = "{}: {}.{} = {}".format(message, form, field, repr(value))
            else:
                message = "{}: {}".format(message, form)
        elif field and value:
            message = "{}: {} = {}".format(message, field, repr(value))
        elif field:
            message = "{}: {}".format(message, field)
        elif value:
            message = "{}: {}".format(message, repr(value))
        super(FormError, self).__init__(message)


class ValidationError(FormError):
    """Raised when form or field validation fails."""
    message = "value is invalid"


class EncodingError(FormError):
    """Raised on field encoding/decoding error."""
    encode_message = "failed to encode value"
    decode_message = "failed to decode value"

    def __init__(self, message=None, form=None, field=None, value=None, encode=True):
        """Format an encoding error message."""
        self.message = encode and self.encode_message or self.decode_message
        super(EncodingError, self).__init__(message, form, field, value)
