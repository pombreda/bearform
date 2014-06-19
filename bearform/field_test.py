"""Test field module."""
import unittest
from bearform.errors import ValidationError
from bearform.field import Field
from bearform.test import TestForm, negative


class FieldTest(unittest.TestCase):
    """Test the Field class."""

    def test_property(self):
        """Field.getter"""
        # get missing attribute
        obj = TestForm()
        obj._attrs = {}
        self.assertRaises(AttributeError, getattr, obj, 'index')

        # get existing attribute
        obj = TestForm(index=5)
        self.assertEquals(obj.index, 5)

        # set value
        obj = TestForm(index=3)
        obj.index = 5
        self.assertEquals(obj.index, 5)

    def test_ensure(self):
        """Field.ensure"""
        field = Field(int)
        field.ensure(negative)

        # valid value
        field.validate(TestForm, 'index', -3)

        # invalid value
        self.assertRaises(ValidationError, field.validate, TestForm, 'index', 3)
