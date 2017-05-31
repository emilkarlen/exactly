import unittest

from exactly_lib.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.symbol.value_resolvers.string_resolvers import StringConstant
from exactly_lib_test.symbol.test_resources import concrete_value_assertions as sut
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestEqualsResolver)


class TestEqualsResolver(unittest.TestCase):
    def test_equals__file_ref(self):
        # ARRANGE #
        value = FileRefConstant(file_ref_test_impl('file-name'))
        # ACT & ASSERT #
        sut.resolver_equals3(value).apply_without_message(self, value)

    def test_equals__string(self):
        # ARRANGE #
        value = StringConstant('string')
        # ACT & ASSERT #
        sut.resolver_equals3(value).apply_without_message(self, value)

    def test_not_equals__different_types(self):
        # ARRANGE #
        expected = FileRefConstant(file_ref_test_impl('file-name'))
        actual = StringConstant('string value')
        put = test_case_with_failure_exception_set_to_test_exception()
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.resolver_equals3(expected).apply_without_message(put, actual)

    def test_not_equals__file_ref(self):
        # ARRANGE #
        expected = FileRefConstant(file_ref_test_impl('expected-file-name'))
        actual = FileRefConstant(file_ref_test_impl('actual-file-name'))
        put = test_case_with_failure_exception_set_to_test_exception()
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.resolver_equals3(expected).apply_without_message(put, actual)

    def test_not_equals__string(self):
        # ARRANGE #
        expected = StringConstant('expected string')
        actual = StringConstant('actual string')
        put = test_case_with_failure_exception_set_to_test_exception()
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.resolver_equals3(expected).apply_without_message(put, actual)
