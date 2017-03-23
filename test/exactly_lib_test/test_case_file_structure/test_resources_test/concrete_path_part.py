import unittest

from exactly_lib_test.test_case_file_structure.test_resources import concrete_path_part as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsPathPartString),
        unittest.makeSuite(TestEqualsPathPartWithSymbolReference),
    ])


class TestEqualsPathPartString(unittest.TestCase):
    def test_fail_when_file_name_is_different(self):
        actual = sut.PathPartAsFixedPath('actual-file-name')
        assertion = sut.equals_path_part_string('expected-file-name')
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            assertion.apply_without_message(put, actual)

    def test_fail_when_actual_object_is_of_wrong_type(self):
        actual = sut.PathPartAsStringSymbolReference('symbol-name')
        assertion = sut.equals_path_part_string('file-name')
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            assertion.apply_without_message(put, actual)

    def test_pass_when_file_name_is_equal(self):
        actual = sut.PathPartAsFixedPath('file-name')
        assertion = sut.equals_path_part_string('file-name')
        put = test_case_with_failure_exception_set_to_test_exception()
        assertion.apply_without_message(put, actual)


class TestEqualsPathPartWithSymbolReference(unittest.TestCase):
    def test_fail_when_symbol_name_is_different(self):
        actual = sut.PathPartAsStringSymbolReference('actual-symbol-name')
        expected = sut.PathPartAsStringSymbolReference('expected-symbol-name')
        assertion = sut.equals_path_part_with_symbol_reference(expected)
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            assertion.apply_without_message(put, actual)

    def test_fail_when_actual_object_is_of_wrong_type(self):
        actual = sut.PathPartAsFixedPath('file-name')
        expected = sut.PathPartAsStringSymbolReference('expected-symbol-name')
        assertion = sut.equals_path_part_with_symbol_reference(expected)
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            assertion.apply_without_message(put, actual)

    def test_pass_when_symbol_name_is_equal(self):
        actual = sut.PathPartAsStringSymbolReference('symbol-name')
        expected = sut.PathPartAsStringSymbolReference('symbol-name')
        assertion = sut.equals_path_part_with_symbol_reference(expected)
        put = test_case_with_failure_exception_set_to_test_exception()
        assertion.apply_without_message(put, actual)
