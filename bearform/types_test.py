"""Test types module."""
import era
from bearform import types
from bearform.errors import EncodingError, ValidationError
from bearform.test import TestCase, TestForm


class TestFieldType(TestCase):
    """Test FieldType class."""

    def setUp(self):
        self.typ = types.FieldType

    def test_supported(self):
        """FieldType.supported"""
        self.assertFalse(self.typ.supported(str))
        self.assertFalse(self.typ.supported(int))
        self.assertFalse(self.typ.supported(None))

    def test_create(self):
        """FieldType.create"""
        value = types.FieldType.create(era.datetime)
        self.assertIsInstance(value, types.DateTimeType)

        want = types.DateType()
        have = types.FieldType.create(want)
        self.assertEqual(have, want)

        value = types.FieldType.create(int)
        self.assertIsInstance(value, types.BuiltinType)
        self.assertEqual(value.builtin, int)

    def test_default(self):
        """FieldType.default"""
        value = 'yep'
        self.assertEqual(self.typ().default(value), value)

    def test_encode(self):
        """FieldType.encode"""
        value = 'yep'
        self.assertEqual(self.typ().encode(TestCase, 'test', value), value)

    def test_decode(self):
        """FieldType.decode"""
        value = 'yep'
        self.assertEqual(self.typ().decode(TestCase, 'test', value), value)

    def test_validate(self):
        """FieldType.validate"""
        self.typ().validate(TestCase, 'test', 'any value')


class TestBuiltinType(TestCase):
    """Test BuiltinType class."""

    def setUp(self):
        self.typ = types.BuiltinType

    def test_init(self):
        """FieldType.__init__"""
        typ = self.typ(str)
        self.assertEqual(typ.builtin, unicode)
        typ = self.typ(int)
        self.assertEqual(typ.builtin, int)

    def test_encode(self):
        """FieldType.encode"""
        def test(builtin, value, want):
            self.assertCall(want, self.typ(builtin).encode, TestForm, 'test', value)

        test(str, 'yep', 'yep')
        test(str, 12, '12')
        test(int, 12, 12)
        test(int, '12', 12)
        test(int, 'nope', EncodingError)

    def test_decode(self):
        """FieldType.decode"""
        def test(builtin, value, want):
            self.assertCall(want, self.typ(builtin).decode, TestForm, 'test', value)

        test(str, 'yep', 'yep')
        test(str, 12, '12')
        test(int, 12, 12)
        test(int, '12', 12)
        test(int, 'nope', EncodingError)


class TestDateType(TestCase):
    """Test DateType class."""

    def setUp(self):
        self.typ = types.DateType

    def test_supported(self):
        """DateType.supported"""
        self.assertTrue(self.typ.supported(era.date))
        self.assertFalse(self.typ.supported(era.datetime))
        self.assertFalse(self.typ.supported(era.time))
        self.assertFalse(self.typ.supported(str))
        self.assertFalse(self.typ.supported('nope'))

    def test_encode(self):
        """DateType.encode"""
        def test(value, want):
            self.assertCall(want, self.typ().encode, TestForm, 'test', value)

        # date
        value = era.now().date()
        want = era.tsms(value)
        test(value, want)

        # datetime
        value = era.now()
        want = era.tsms(era.truncate(value, era.day))
        test(value, want)

        # time (fail)
        value = era.now().time()
        test(value, EncodingError)

        # str (fail)
        test('nope', EncodingError)

    def test_decode(self):
        """DateType.decode"""
        def test(value, want):
            self.assertCall(want, self.typ().decode, TestForm, 'test', value)

        # integer
        now = era.now()
        want = now.date()
        value = era.tsms(now)
        test(value, want)

        # string
        test(str(value), want)

        # invalid
        test('nope', EncodingError)


class TestDateTimeType(TestCase):
    """Test DateTimeType class."""

    def setUp(self):
        self.typ = types.DateTimeType

    def test_supported(self):
        """DateTimeType.supported"""
        self.assertTrue(self.typ.supported(era.datetime))
        self.assertFalse(self.typ.supported(era.date))
        self.assertFalse(self.typ.supported(era.time))
        self.assertFalse(self.typ.supported(str))
        self.assertFalse(self.typ.supported('nope'))

    def test_encode(self):
        """DateTimeType.encode"""
        def test(value, want):
            self.assertCall(want, self.typ().encode, TestForm, 'test', value)

        # date
        value = era.now().date()
        want = era.tsms(value)
        test(value, want)

        # datetime
        value = era.now()
        want = era.tsms(value)
        test(value, want)

        # time
        value = era.now().time()
        want = era.tsms(value)
        test(value, want)

        # str (fail)
        test('nope', EncodingError)

    def test_decode(self):
        """DateTimeType.decode"""
        def test(value, want):
            self.assertCall(want, self.typ().decode, TestForm, 'test', value)

        # integer
        want = era.truncate(era.now(), era.millisecond)
        value = era.tsms(want)
        test(value, want)

        # string
        test(str(value), want)

        # invalid
        test('nope', EncodingError)


class TestTimeType(TestCase):
    """Test TimeType class."""

    def setUp(self):
        self.typ = types.TimeType

    def test_supported(self):
        """TimeType.supported"""
        self.assertTrue(self.typ.supported(era.time))
        self.assertFalse(self.typ.supported(era.date))
        self.assertFalse(self.typ.supported(era.datetime))
        self.assertFalse(self.typ.supported(str))
        self.assertFalse(self.typ.supported('nope'))

    def test_encode(self):
        """TimeType.encode"""
        def test(value, want):
            self.assertCall(want, self.typ().encode, TestForm, 'test', value)

        # time
        value = era.now().time()
        want = era.tsms(value)
        test(value, want)

        # datetime
        value = era.now()
        want = era.tsms(value.time())
        test(value, want)

        # date (fail)
        value = era.now().date()
        test(value, EncodingError)

        # str (fail)
        test('nope', EncodingError)

    def test_decode(self):
        """TimeType.decode"""
        def test(value, want):
            self.assertCall(want, self.typ().decode, TestForm, 'test', value)

        # integer
        now = era.truncate(era.now(), era.millisecond)
        want = now.time()
        value = era.tsms(now)
        test(value, want)

        # string
        test(str(value), want)

        # invalid
        test('nope', EncodingError)


class TestFormType(TestCase):
    """Test FormType class."""

    def setUp(self):
        self.typ = types.FormType
        self.obj = types.FormType(TestForm)

    def test_supported(self):
        """FormType.supported"""
        self.assertTrue(self.typ.supported(TestForm))
        self.assertFalse(self.typ.supported(object))
        self.assertFalse(self.typ.supported('nope'))

    def test_default(self):
        """FormType.default"""
        want = TestForm().encode()
        have = self.typ(TestForm).default(None)
        self.assertEqual(have, want)

    def test_encode(self):
        """FormType.encode"""
        def test(value, want):
            self.assertCall(want, self.typ(TestForm).encode, TestForm, 'test', value)

        # no encoding needed
        value = {'index': 1, 'name': 'one', 'optional': 'present'}
        want = value.copy()
        test(value, want)

        # needs encoding
        value = {'index': '1', 'name': 'one', 'optional': 'present'}
        want = {'index': 1, 'name': 'one', 'optional': 'present'}
        test(value, want)

        # missing optional
        value = {'index': '1', 'name': 'one'}
        want = {'index': 1, 'name': 'one', 'optional': 'missing'}
        test(value, want)

        # invalid
        test('nope', EncodingError)

    def test_decode(self):
        """FormType.decode"""
        def test(value, want):
            self.assertCall(want, self.typ(TestForm).decode, TestForm, 'test', value)

        # no decoding needed
        value = {'index': 1, 'name': 'one', 'optional': 'present'}
        want = value.copy()
        test(value, want)

        # needs decoding
        value = {'index': '1', 'name': 'one', 'optional': 'present'}
        want = {'index': 1, 'name': 'one', 'optional': 'present'}
        test(value, want)

        # missing optional
        value = {'index': '1', 'name': 'one'}
        want = {'index': 1, 'name': 'one', 'optional': 'missing'}
        test(value, want)

        # invalid
        test('nope', EncodingError)

    def test_validate(self):
        """FormType.validate"""
        def test(value, want):
            self.assertCall(want, self.typ(TestForm).validate, TestForm, 'test', value)

        # valid data
        value = {'index': 1, 'name': 'one', 'optional': 'present'}
        test(value, None)

        # invalid data
        value = {'index': -1, 'name': 'one', 'optional': 'present'}
        test(value, ValidationError)


class ListTypeTest(TestCase):
    """Test ListType class."""

    def setUp(self):
        self.typ = types.ListType

    def test_init(self):
        """ListType.__init__"""
        # valid type
        self.assertEqual(self.typ([int]).typ.builtin, int)

        # none type
        self.assertIsNone(self.typ(None).typ)

        # invalid type
        self.assertRaises(TypeError, self.typ, {int})

    def test_supported(self):
        """ListType.supported"""
        self.assertTrue(self.typ.supported(list))
        self.assertTrue(self.typ.supported([]))
        self.assertTrue(self.typ.supported([int]))
        self.assertFalse(self.typ.supported(object))
        self.assertFalse(self.typ.supported('nope'))

    def test_encode(self):
        """ListType.encode"""
        def test(t, value, want):
            self.assertCall(want, self.typ(t).encode, TestForm, 'test', value)

        # free-form list
        value = ['a', 'b', 1]
        want = list(value)
        test(list, value, want)

        # typed list
        value = ['a', 'b', 1]
        want = ['a', 'b', '1']
        test([str], value, want)

        # other iterator
        test([str], tuple(value), want)

        # invalid
        value = ['a', 'b', 1]
        test([int], value, EncodingError)

    def test_decode(self):
        """ListType.decode"""
        def test(t, value, want):
            self.assertCall(want, self.typ(t).decode, TestForm, 'test', value)

        # free-form list
        value = ['a', 'b', 1]
        want = list(value)
        test(list, value, want)

        # typed list
        value = ['a', 'b', 1]
        want = ['a', 'b', '1']
        test([str], value, want)

        # invalid
        value = ['a', 'b', 1]
        test([int], value, EncodingError)


class SetTypeTest(TestCase):
    """Test SetType class."""

    def setUp(self):
        self.typ = types.SetType

    def test_init(self):
        """SetType.__init__"""
        # valid type
        self.assertEqual(self.typ({int}).typ.builtin, int)

        # none type
        self.assertIsNone(self.typ(None).typ)

        # invalid type
        self.assertRaises(TypeError, self.typ, [int])

    def test_supported(self):
        """SetType.supported"""
        self.assertTrue(self.typ.supported(set))
        self.assertTrue(self.typ.supported(set()))
        self.assertTrue(self.typ.supported({int}))
        self.assertFalse(self.typ.supported(object))
        self.assertFalse(self.typ.supported('nope'))

    def test_encode(self):
        """SetType.encode"""
        def test(t, value, want):
            def func():
                return sorted(self.typ(t).encode(TestForm, 'test', value))
            self.assertCall(want, func)

        # free-form set
        value = {'a', 'b', 1}
        want = sorted(value)
        test(set, value, want)

        # typed set
        value = {'a', 'b', 1}
        want = sorted(['a', 'b', '1'])
        test({str}, value, want)

        # other iterator
        test({str}, list(value), want)

        # invalid
        value = {'a', 'b', 1}
        test({int}, value, EncodingError)

    def test_decode(self):
        """SetType.decode"""
        def test(t, value, want):
            def func():
                return sorted(self.typ(t).decode(TestForm, 'test', value))
            self.assertCall(want, func)

        # free-form set
        value = {'a', 'b', 1}
        want = sorted(value)
        test(set, value, want)

        # typed set
        value = {'a', 'b', 1}
        want = sorted(['a', 'b', '1'])
        test({str}, value, want)

        # other iterator
        test({str}, list(value), want)

        # invalid
        value = {'a', 'b', 1}
        test({int}, value, EncodingError)


class DictTypeTest(TestCase):
    """Test DictType class."""

    def setUp(self):
        self.typ = types.DictType

    def test_supported(self):
        """DictType.supported"""
        self.assertTrue(self.typ.supported(dict))
        self.assertTrue(self.typ.supported({}))
        self.assertTrue(self.typ.supported({'_': int}))
        self.assertFalse(self.typ.supported(object))
        self.assertFalse(self.typ.supported('nope'))

    def test_init(self):
        """DictType.__init__"""
        # valid type
        self.assertEqual(self.typ({None: int}).typ.builtin, int)

        # none type
        self.assertIsNone(self.typ(None).typ)

        # invalid type
        self.assertRaises(TypeError, self.typ, [int])

    def test_encode(self):
        """DictType.encode"""
        def test(t, value, want):
            self.assertCall(want, self.typ(t).encode, TestForm, 'test', value)

        # free-form dict
        value = {'a': 'aye', 'b': 'bee', 'one': 1}
        want = value.copy()
        test(dict, value, want)

        # typed dict
        value = {'a': 'aye', 'b': 'bee', 'one': 1}
        want = {'a': 'aye', 'b': 'bee', 'one': '1'}
        test({None: str}, value, want)

        # invalid
        value = {'a': 'aye', 'b': 'bee', 'one': 1}
        test({None: int}, value, EncodingError)

    def test_decode(self):
        """DictType.decode"""
        def test(t, value, want):
            self.assertCall(want, self.typ(t).decode, TestForm, 'test', value)

        # free-form dict
        value = {'a': 'aye', 'b': 'bee', 'one': 1}
        want = value.copy()
        test(dict, value, want)

        # typed dict
        value = {'a': 'aye', 'b': 'bee', 'one': 1}
        want = {'a': 'aye', 'b': 'bee', 'one': '1'}
        test({None: str}, value, want)

        # invalid
        value = {'a': 'aye', 'b': 'bee', 'one': 1}
        test({None: int}, value, EncodingError)
