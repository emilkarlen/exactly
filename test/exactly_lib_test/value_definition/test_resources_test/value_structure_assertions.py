import unittest

from exactly_lib.value_definition.concrete_values import StringValue, FileRefValue
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.value_definition.test_resources import concrete_value_assertion as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsString),
        unittest.makeSuite(TestEqualsFileRef),
    ])


class TestEqualsString(unittest.TestCase):
    def test_equals(self):
        # ARRANGE #
        value = StringValue('s')
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


class TestEqualsFileRef(unittest.TestCase):
    def test_equals(self):
        # ARRANGE #
        value = FileRefValue(file_ref_test_impl('file-name'))
        sut.equals_file_ref_value(value).apply_without_message(self, value)

    def test_not_equals__different_file_name(self):
        # ARRANGE #
        expected = FileRefValue(file_ref_test_impl('expected-file-name'))
        actual = FileRefValue(file_ref_test_impl('actual-file-name'))
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            sut.equals_file_ref_value(expected).apply_without_message(put, actual)

    def test_not_equals__different_type(self):
        # ARRANGE #
        expected = FileRefValue(file_ref_test_impl('file-name'))
        actual = StringValue('expected string')
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            sut.equals_file_ref_value(expected).apply_without_message(put, actual)
