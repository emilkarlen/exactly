import unittest

from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.value_definition.concrete_restrictions import NoRestriction
from exactly_lib.value_definition.concrete_values import StringValue, FileRefValue
from exactly_lib.value_definition.value_structure import ValueReference
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.value_definition.test_resources import concrete_value_assertion as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsString),
        unittest.makeSuite(TestEqualsFileRef),
        unittest.makeSuite(TestEqualsValue),
    ])


class TestEqualsString(unittest.TestCase):
    def test_equals__without_references(self):
        # ARRANGE #
        value = StringValue('s')
        sut.equals_string_value(value).apply_without_message(self, value)

    def test_equals__with_references(self):
        # ARRANGE #
        value = _StringValueTestImpl('s',
                                     [ValueReference('symbol_name',
                                                     NoRestriction())])
        sut.equals_string_value(value).apply_without_message(self, value)

    def test_not_equals__different_string(self):
        # ARRANGE #
        expected = StringValue('expected string')
        actual = StringValue('actual string')
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            sut.equals_string_value(expected).apply_without_message(put, actual)

    def test_not_equals__different_type(self):
        # ARRANGE #
        expected = StringValue('expected string')
        actual = FileRefValue(file_ref_test_impl('file-name'))
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            sut.equals_string_value(expected).apply_without_message(put, actual)

    def test_not_equals__different_references__different_references(self):
        # ARRANGE #
        value = 'string value'
        expected = _StringValueTestImpl(value,
                                        [ValueReference('expected_symbol_name',
                                                        NoRestriction())])
        actual = _StringValueTestImpl(value,
                                      [ValueReference('actual_symbol_name',
                                                      NoRestriction())]
                                      )
        put = test_case_with_failure_exception_set_to_test_exception()
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_string_value(expected).apply_without_message(put, actual)


class TestEqualsFileRef(unittest.TestCase):
    def test_equals__without_references(self):
        # ARRANGE #
        value = FileRefValue(file_ref_test_impl('file-name'))
        # ACT & ASSERT #
        sut.equals_file_ref_value(value).apply_without_message(self, value)

    def test_equals__with_references(self):
        # ARRANGE #
        value = _FileRefValueTestImpl(file_ref_test_impl('file-name'),
                                      [ValueReference('symbol_name', NoRestriction())])
        # ACT & ASSERT #
        sut.equals_file_ref_value(value).apply_without_message(self, value)

    def test_not_equals__different_file_name(self):
        # ARRANGE #
        expected = FileRefValue(file_ref_test_impl('expected-file-name'))
        actual = FileRefValue(file_ref_test_impl('actual-file-name'))
        put = test_case_with_failure_exception_set_to_test_exception()
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_file_ref_value(expected).apply_without_message(put, actual)

    def test_not_equals__different_type(self):
        # ARRANGE #
        expected = FileRefValue(file_ref_test_impl('file-name'))
        actual = StringValue('expected string')
        put = test_case_with_failure_exception_set_to_test_exception()
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_file_ref_value(expected).apply_without_message(put, actual)

    def test_not_equals__different_references__different_number_of_references(self):
        # ARRANGE #
        file_ref = file_ref_test_impl('file-name')
        expected = _FileRefValueTestImpl(file_ref,
                                         [ValueReference('symbol_name',
                                                         NoRestriction())])
        actual = _FileRefValueTestImpl(file_ref, [])
        put = test_case_with_failure_exception_set_to_test_exception()
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_file_ref_value(expected).apply_without_message(put, actual)

    def test_not_equals__different_references__different_references(self):
        # ARRANGE #
        file_ref = file_ref_test_impl('file-name')
        expected = _FileRefValueTestImpl(file_ref,
                                         [ValueReference('expected_symbol_name',
                                                         NoRestriction())])
        actual = _FileRefValueTestImpl(file_ref,
                                       [ValueReference('actual_symbol_name',
                                                       NoRestriction())]
                                       )
        put = test_case_with_failure_exception_set_to_test_exception()
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_file_ref_value(expected).apply_without_message(put, actual)


class TestEqualsValue(unittest.TestCase):
    def test_equals__file_ref(self):
        # ARRANGE #
        value = FileRefValue(file_ref_test_impl('file-name'))
        # ACT & ASSERT #
        sut.equals_value(value).apply_without_message(self, value)

    def test_equals__string(self):
        # ARRANGE #
        value = StringValue('string')
        # ACT & ASSERT #
        sut.equals_value(value).apply_without_message(self, value)

    def test_not_equals__different_types(self):
        # ARRANGE #
        expected = FileRefValue(file_ref_test_impl('file-name'))
        actual = StringValue('string value')
        put = test_case_with_failure_exception_set_to_test_exception()
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_value(expected).apply_without_message(put, actual)

    def test_not_equals__file_ref(self):
        # ARRANGE #
        expected = FileRefValue(file_ref_test_impl('expected-file-name'))
        actual = FileRefValue(file_ref_test_impl('actual-file-name'))
        put = test_case_with_failure_exception_set_to_test_exception()
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_value(expected).apply_without_message(put, actual)

    def test_not_equals__string(self):
        # ARRANGE #
        expected = StringValue('expected string')
        actual = StringValue('actual string')
        put = test_case_with_failure_exception_set_to_test_exception()
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_value(expected).apply_without_message(put, actual)


class _FileRefValueTestImpl(FileRefValue):
    def __init__(self,
                 file_ref: FileRef,
                 explicit_references: list):
        super().__init__(file_ref)
        self.explicit_references = explicit_references

    @property
    def file_ref(self) -> FileRef:
        return self._file_ref

    @property
    def references(self) -> list:
        return self.explicit_references


class _StringValueTestImpl(StringValue):
    def __init__(self,
                 value: str,
                 explicit_references: list):
        super().__init__(value)
        self.explicit_references = explicit_references

    @property
    def references(self) -> list:
        return self.explicit_references
