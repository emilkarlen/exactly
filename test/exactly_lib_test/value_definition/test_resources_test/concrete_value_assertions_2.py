import unittest

from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.value_definition.concrete_values import StringValue, FileRefValue
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.value_definition.test_resources import concrete_value_assertions_2 as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestEqualsValue)


class TestEqualsValue(unittest.TestCase):
    def test_equals__file_ref(self):
        # ARRANGE #
        value = FileRefValue(file_ref_test_impl('file-name'))
        # ACT & ASSERT #
        sut.value_equals3(value).apply_without_message(self, value)

    def test_equals__string(self):
        # ARRANGE #
        value = StringValue('string')
        # ACT & ASSERT #
        sut.value_equals3(value).apply_without_message(self, value)

    def test_not_equals__different_types(self):
        # ARRANGE #
        expected = FileRefValue(file_ref_test_impl('file-name'))
        actual = StringValue('string value')
        put = test_case_with_failure_exception_set_to_test_exception()
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.value_equals3(expected).apply_without_message(put, actual)

    def test_not_equals__file_ref(self):
        # ARRANGE #
        expected = FileRefValue(file_ref_test_impl('expected-file-name'))
        actual = FileRefValue(file_ref_test_impl('actual-file-name'))
        put = test_case_with_failure_exception_set_to_test_exception()
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.value_equals3(expected).apply_without_message(put, actual)

    def test_not_equals__string(self):
        # ARRANGE #
        expected = StringValue('expected string')
        actual = StringValue('actual string')
        put = test_case_with_failure_exception_set_to_test_exception()
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.value_equals3(expected).apply_without_message(put, actual)


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
