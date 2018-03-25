import unittest

from exactly_lib.symbol.data import file_ref_resolvers2, list_resolvers
from exactly_lib.symbol.data.string_resolvers import str_constant
from exactly_lib_test.symbol.data.test_resources import any_resolver_assertions as sut
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils as su
from exactly_lib_test.symbol.test_resources.file_matcher import FileMatcherResolverConstantTestImpl
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.type_system.data.test_resources.file_matcher import FileMatcherThatSelectsAllFilesTestImpl


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestEqualsResolver)


class TestEqualsResolver(unittest.TestCase):
    def test_equals__file_ref(self):
        # ARRANGE #
        value = file_ref_resolvers2.constant(file_ref_test_impl('file-name'))
        # ACT & ASSERT #
        sut.equals_resolver(value).apply_without_message(self, value)

    def test_equals__string(self):
        # ARRANGE #
        value = str_constant('string')
        # ACT & ASSERT #
        sut.equals_resolver(value).apply_without_message(self, value)

    def test_equals__list(self):
        # ARRANGE #
        value = list_resolvers.from_str_constants(['value'])
        # ACT & ASSERT #
        sut.equals_resolver(value).apply_without_message(self, value)

    def test_not_equals__different_symbol_types(self):
        # ARRANGE #
        expected = file_ref_resolvers2.constant(file_ref_test_impl('file-name'))
        actual = str_constant('string value')
        # ACT & ASSERT #
        assert_that_assertion_fails(sut.equals_resolver(expected), actual)

    def test_not_equals__non_symbol_type(self):
        # ARRANGE #
        expected = file_ref_resolvers2.constant(file_ref_test_impl('file-name'))
        actual = FileMatcherResolverConstantTestImpl(FileMatcherThatSelectsAllFilesTestImpl())
        # ACT & ASSERT #
        assert_that_assertion_fails(sut.equals_resolver(expected), actual)

    def test_not_equals__file_ref(self):
        # ARRANGE #
        expected = file_ref_resolvers2.constant(file_ref_test_impl('expected-file-name'))
        actual = file_ref_resolvers2.constant(file_ref_test_impl('actual-file-name'))
        # ACT & ASSERT #
        assert_that_assertion_fails(sut.equals_resolver(expected), actual)

    def test_not_equals__string(self):
        # ARRANGE #
        expected = str_constant('expected string')
        actual = str_constant('actual string')
        # ACT & ASSERT #
        assert_that_assertion_fails(sut.equals_resolver(expected), actual)

    def test_not_equals__list(self):
        # ARRANGE #
        expected = list_resolvers.from_str_constants(['value'])
        actual = list_resolvers.from_elements([list_resolvers.symbol_element(su.symbol_reference('symbol_name'))])
        # ACT & ASSERT #
        assert_that_assertion_fails(sut.equals_resolver(expected), actual)
