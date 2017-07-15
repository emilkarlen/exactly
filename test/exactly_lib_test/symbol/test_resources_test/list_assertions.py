import unittest

from exactly_lib.symbol import list_resolver
from exactly_lib.symbol import string_resolver as sr
from exactly_lib_test.symbol.test_resources import list_assertions as sut
from exactly_lib_test.symbol.test_resources.symbol_utils import symbol_reference
from exactly_lib_test.test_resources.value_assertions.assert_that_assertion_fails import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsElement),
    ])


class TestEqualsElement(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            list_resolver.StringResolverElement(sr.string_constant('value')),
            list_resolver.SymbolReferenceElement(symbol_reference('symbol_name')),
        ]
        for element in test_cases:
            with self.subTest(msg=str(element)):
                sut.equals_list_resolver_element(element).apply_without_message(self, element)

    def test_string_not_equals_symbol_ref(self):
        # ARRANGE #
        string_element = list_resolver.StringResolverElement(sr.string_constant('value'))
        symbol_reference_element = list_resolver.SymbolReferenceElement(symbol_reference('symbol_name'))
        assertion = sut.equals_list_resolver_element(string_element)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, symbol_reference_element)

    def test_symbol_ref_not_equals_string(self):
        # ARRANGE #
        string_element = list_resolver.StringResolverElement(sr.string_constant('value'))
        symbol_reference_element = list_resolver.SymbolReferenceElement(symbol_reference('symbol_name'))
        assertion = sut.equals_list_resolver_element(symbol_reference_element)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, string_element)

    def test_string_not_equals_string_with_different_value(self):
        # ARRANGE #
        expected = list_resolver.StringResolverElement(sr.string_constant('expected value'))
        actual = list_resolver.StringResolverElement(sr.string_constant('actual value'))
        assertion = sut.equals_list_resolver_element(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_symbol_ref_not_equals_symbol_ref_with_different_symbol_name(self):
        # ARRANGE #
        expected = list_resolver.SymbolReferenceElement(symbol_reference('expected_symbol_name'))
        actual = list_resolver.SymbolReferenceElement(symbol_reference('actual_symbol_name'))
        assertion = sut.equals_list_resolver_element(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)
