"""Test meta module."""
import unittest
from common import TestForm


class MetaTest(unittest.TestCase):
    """Test the form meta classes."""

    def test_options(self):
        """Form._meta.options"""
        self.assertTrue(TestForm._meta.options, {'value': 'value'})
