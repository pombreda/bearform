"""Common test utilities."""
import unittest
from bearform.errors import ValidationError
from bearform.field import Field
from bearform.form import Form


def is_exception(value):
    return isinstance(value, type) and issubclass(value, Exception)


def positive(form, name, value):
    if value < 0:
        raise ValidationError("{}.{} must be positive".format(form.__name__, name))


def negative(form, name, value):
    if value >= 0:
        raise ValidationError("{}.{} must be negative".format(form.__name__, name))


class TestForm(Form):
    class Meta:
        value = 'value'

    index = Field(int, validators=[positive])
    name = Field(str)
    optional = Field(str, require=False, default='missing')


class TestSubForm(Form):
    name = Field(str)


class TestTopForm(Form):
    sub = Field(TestSubForm)


class TestCase(unittest.TestCase):

    def assertCall(self, want, func, *args, **kwargs):
        if is_exception(want):
            self.assertRaises(want, func, *args, **kwargs)
        else:
            have = func(*args, **kwargs)
            self.assertEqual(have, want)
