"""Test form module."""
from bearform.errors import ValidationError
from bearform.utils import Struct
from common import TestCase, TestForm, TestTopForm, TestListForm, TestDictForm


class FormTest(TestCase):
    """Test for Form class."""

    def test_from_obj(self):
        """Form.from_obj"""
        class Data(object):
            def __init__(self, index, name):
                self.index = index
                self.name = name

        obj = Data('1', 'object')
        form = TestForm.from_obj(obj)
        self.assertEqual(form.index, obj.index)
        self.assertEqual(form.name, obj.name)
        self.assertEqual(form.optional, 'missing')

        data = form.encode()
        self.assertEqual(data, {'index': 1, 'name': 'object', 'optional': 'missing'})

        class TopData(object):
            def __init__(self, sub):
                self.sub = sub

        class SubData(object):
            def __init__(self, name):
                self.name = name

        obj = TopData(SubData('test'))
        form = TestTopForm.from_obj(obj)
        self.assertEqual(form.sub, {'name': 'test'})

        data = form.encode()
        self.assertEqual(data, {'sub': {'name': 'test'}})

        class CollectionData(object):
            def __init__(self, sub):
                self.subs = sub

        obj = CollectionData([SubData('test1'), SubData('test2')])
        form = TestListForm.from_obj(obj)
        self.assertEqual(form.subs, [{'name': 'test1'}, {'name': 'test2'}])

        data = form.encode()
        self.assertEqual(data, {'subs': [{'name': 'test1'}, {'name': 'test2'}]})

        obj = CollectionData({'one': SubData('test1'), 'two': SubData('test2')})
        form = TestDictForm.from_obj(obj)
        self.assertEqual(form.subs, {'one': {'name': 'test1'}, 'two': {'name': 'test2'}})

        data = form.encode()
        self.assertEqual(data, {'subs': {'one': {'name': 'test1'}, 'two': {'name': 'test2'}}})

    def test_decode(self):
        """Form.decode"""
        def test(value, want, **options):
            def func():
                return TestForm.decode(value, **options)._attrs
            self.assertCall(want, func)

        # with all values
        want = {'index': 1, 'name': 'first', 'optional': 'here'}
        value = want.copy()
        test(value, want)

        # with missing form data
        value = {'name': 'first', 'optional': 'here'}
        test(value, ValidationError)

        # with extra form data
        value = {'index': 1, 'name': 'first', 'optional': 'here', 'unknown': 'yes'}
        test(value, ValidationError)

        # with extra form data ignored
        value = {'index': 1, 'name': 'first', 'optional': 'here', 'unknown': 'yes'}
        want = {'index': 1, 'name': 'first', 'optional': 'here'}
        test(value, want, extra=True)

        # with extra form data defined
        test(value, want, extra=['unknown'])

        # with incorrect extra form data defined
        test(value, ValidationError, extra=['known'])

        # without optional form data
        want = {'index': 1, 'name': 'first', 'optional': 'missing'}
        value = {'index': 1, 'name': 'first'}
        test(value, want)

        # with data that requires encoding
        want = {'index': 1, 'name': 'first', 'optional': 'here'}
        value = {'index': '1', 'name': 'first', 'optional': 'here'}
        test(value, want)

        # with invalid fields with validation enabled
        value = {'index': -3, 'name': 'first', 'optional': 'here'}
        test(value, ValidationError)

        # with invalid fields with validation disabled
        want = {'index': -3, 'name': 'first', 'optional': 'here'}
        value = want.copy()
        test(value, want, validate=False)

    def test_init(self):
        """Form.__init__"""
        # empty init
        value = {'index': None, 'name': None, 'optional': 'missing'}
        self.assertEqual(TestForm()._attrs, value)

        # init with valid values
        value = {'index': 2, 'name': 'second', 'optional': 'present'}
        self.assertEqual(TestForm(**value)._attrs, value)

        # init with invalid values
        value = {'index': -3, 'name': 'second', 'optional': 'present'}
        self.assertEqual(TestForm(**value)._attrs, value)

        # init with extra values
        value = {'index': 2, 'name': 'second', 'optional': 'present', 'unknown': 'yes'}
        want = {'index': 2, 'name': 'second', 'optional': 'present'}
        form = TestForm(**value)
        self.assertEqual(form._attrs, want)
        self.assertEqual(form.unknown, 'yes')

        # init with missing values
        value = {'index': 2}
        want = {'index': 2, 'name': None, 'optional': 'missing'}
        self.assertEqual(TestForm(**value)._attrs, want)

    def test_encode(self):
        """Form.encode"""
        def test(value, want, *args, **kwargs):
            form = TestForm(**value)
            self.assertCall(want, form.encode, *args, **kwargs)

        # with all values
        value = {'index': 3, 'name': 'third', 'optional': 'present'}
        want = value.copy()
        test(value, want)

        # with missing form data
        value = {'index': 3}
        want = {'index': 3, 'name': None, 'optional': 'missing'}
        test(value, want, True)

        value = {'index': 3}
        want = {'index': 3, 'optional': 'missing'}
        test(value, want)

        # with extra form data
        value = {'index': 3, 'name': 'third', 'optional': 'present', 'unknown': 'yes'}
        want = {'index': 3, 'name': 'third', 'optional': 'present'}
        test(value, want)

        # without optional form data
        value = {'index': 3, 'name': 'third'}
        want = {'index': 3, 'name': 'third', 'optional': 'missing'}
        test(value, want)

        # with data that requires encoding
        value = {'index': '3', 'name': 'third', 'optional': 'present'}
        want = {'index': 3, 'name': 'third', 'optional': 'present'}
        test(value, want)

        # with invalid data
        value = {'index': -3, 'name': 'third', 'optional': 'present'}
        want = {'index': -3, 'name': 'third', 'optional': 'present'}
        test(value, want)

    def test_validate(self):
        """Form.validate"""
        def test(value, valid):
            form = TestForm(**value)
            if valid:
                form.validate()
            else:
                self.assertRaises(ValidationError, form.validate)

        # test valid field
        test({'index': 4, 'name': 'fourth'}, True)

        # test invalid field
        test({'index': -4, 'name': 'fourth'}, False)

        # test missing field
        test({'index': 4}, False)

    def test_to_dict(self):
        """Form.to_dict"""
        value = {'index': 5, 'name': 'fifth', 'optional': 'present'}
        form = TestForm(**value)
        have = form.to_dict()
        self.assertEqual(have, value)

    def test_to_obj(self):
        """Form.to_obj"""
        value = {'index': 6, 'name': 'sixth', 'optional': 'present'}
        want = Struct(**value)
        form = TestForm(**value)

        # create new object
        have = form.to_obj()
        self.assertEqual(vars(have), vars(want))

        # update existing object
        have = Struct(index=12, name='nope')
        form.to_obj(have)
        self.assertEqual(vars(have), vars(want))

    def test_to_obj_subform(self):
        """Form.to_obj with subform"""
        def struct_vars(data):
            data = vars(data)
            if 'sub' in data and hasattr(data['sub'], '__dict__'):
                data['sub'] = vars(data['sub'])

        value = {'sub': {'name': 'subform'}}
        want = Struct(sub=Struct(name='subform'))
        form = TestTopForm(**value)

        # create new object
        have = form.to_obj()
        self.assertEqual(struct_vars(have), struct_vars(want))

        # update existing object
        have = Struct(sub=None)
        form.to_obj(have)
        self.assertEqual(struct_vars(have), struct_vars(want))
