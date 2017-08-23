import unittest

from exactly_lib.named_element.file_selector import FileSelectorConstant
from exactly_lib.named_element.symbol import string_resolver as sr, list_resolver as lr
from exactly_lib.named_element.symbol.string_resolver import string_constant
from exactly_lib.named_element.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.type_system_values.file_selector import FileSelector
from exactly_lib.util import dir_contents_selection
from exactly_lib_test.named_element.symbol.test_resources import any_resolver_assertions as sut
from exactly_lib_test.named_element.symbol.test_resources import symbol_utils as su
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails


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

    def test_equals__list(self):
        # ARRANGE #
        value = lr.ListResolver([lr.StringResolverElement(sr.string_constant('value'))])
        # ACT & ASSERT #
        sut.equals_resolver(value).apply_without_message(self, value)

    def test_not_equals__different_symbol_types(self):
        # ARRANGE #
        expected = FileRefConstant(file_ref_test_impl('file-name'))
        actual = string_constant('string value')
        # ACT & ASSERT #
        assert_that_assertion_fails(sut.equals_resolver(expected), actual)

    def test_not_equals__non_symbol_type(self):
        # ARRANGE #
        expected = FileRefConstant(file_ref_test_impl('file-name'))
        actual = FileSelectorConstant(FileSelector(dir_contents_selection.all_files()))
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

    def test_not_equals__list(self):
        # ARRANGE #
        expected = lr.ListResolver([lr.StringResolverElement(sr.string_constant('value'))])
        actual = lr.ListResolver([lr.SymbolReferenceElement(su.symbol_reference('symbol_name'))])
        # ACT & ASSERT #
        assert_that_assertion_fails(sut.equals_resolver(expected), actual)
