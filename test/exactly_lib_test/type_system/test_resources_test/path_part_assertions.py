import unittest

from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.type_system.test_resources import path_part_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsPathPartString),
        unittest.makeSuite(TestEqualsPathPart),
    ])


class TestEqualsPathPartString(unittest.TestCase):
    def test_fail_when_file_name_is_different(self):
        actual = sut.PathPartAsFixedPath('actual-file-name')
        assertion = sut.equals_path_part_string('expected-file-name')
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            assertion.apply_without_message(put, actual)

    def test_fail_when_actual_object_is_of_wrong_type(self):
        actual = sut.PathPartAsNothing()
        assertion = sut.equals_path_part_string('file-name')
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            assertion.apply_without_message(put, actual)

    def test_pass_when_file_name_is_equal(self):
        actual = sut.PathPartAsFixedPath('file-name')
        assertion = sut.equals_path_part_string('file-name')
        put = test_case_with_failure_exception_set_to_test_exception()
        assertion.apply_without_message(put, actual)


class TestEqualsPathPart(unittest.TestCase):
    def test_pass(self):
        test_cases = [
            sut.PathPartAsFixedPath('actual-file-name'),
        ]
        for value in test_cases:
            with self.subTest():
                assertion = sut.equals_path_part(value)
                assertion.apply_without_message(self, value)
