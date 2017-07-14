import unittest

from exactly_lib.symbol.string_resolver import string_constant
from exactly_lib.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib_test.symbol.test_resources import concrete_value_assertions as sut
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl
from exactly_lib_test.test_resources.value_assertions.assert_that_assertion_fails import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestEqualsResolver)


class TestEqualsResolver(unittest.TestCase):
    def test_equals__file_ref(self):
        # ARRANGE #
        value = FileRefConstant(file_ref_test_impl('file-name'))
        # ACT & ASSERT #
        sut.equals_resolver(value).apply_without_message(self, value)

    def test_equals__string(self):
        # ARRANGE #
        value = string_constant('string')
        # ACT & ASSERT #
        sut.equals_resolver(value).apply_without_message(self, value)

    def test_not_equals__different_types(self):
        # ARRANGE #
        expected = FileRefConstant(file_ref_test_impl('file-name'))
        actual = string_constant('string value')
        # ACT & ASSERT #
        assert_that_assertion_fails(sut.equals_resolver(expected), actual)

    def test_not_equals__file_ref(self):
        # ARRANGE #
        expected = FileRefConstant(file_ref_test_impl('expected-file-name'))
        actual = FileRefConstant(file_ref_test_impl('actual-file-name'))
        # ACT & ASSERT #
        assert_that_assertion_fails(sut.equals_resolver(expected), actual)

    def test_not_equals__string(self):
        # ARRANGE #
        expected = string_constant('expected string')
        actual = string_constant('actual string')
        # ACT & ASSERT #
        assert_that_assertion_fails(sut.equals_resolver(expected), actual)
