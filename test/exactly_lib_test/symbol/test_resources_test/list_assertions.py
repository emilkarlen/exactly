import unittest

from exactly_lib.symbol import list_resolver as lr
from exactly_lib.symbol import string_resolver as sr
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import list_assertions as sut, symbol_utils as su
from exactly_lib_test.symbol.test_resources.symbol_utils import symbol_reference
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions.assert_that_assertion_fails import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsElement),
        unittest.makeSuite(TestEqualsResolver),
    ])


class TestEqualsElement(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            lr.StringResolverElement(sr.string_constant('value')),
            lr.SymbolReferenceElement(symbol_reference('symbol_name')),
        ]
        for element in test_cases:
            with self.subTest(msg=str(element)):
                sut.equals_list_resolver_element(element).apply_without_message(self, element)

    def test_string_not_equals_symbol_ref(self):
        # ARRANGE #
        string_element = lr.StringResolverElement(sr.string_constant('value'))
        symbol_reference_element = lr.SymbolReferenceElement(symbol_reference('symbol_name'))
        assertion = sut.equals_list_resolver_element(string_element)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, symbol_reference_element)

    def test_symbol_ref_not_equals_string(self):
        # ARRANGE #
        string_element = lr.StringResolverElement(sr.string_constant('value'))
        symbol_reference_element = lr.SymbolReferenceElement(symbol_reference('symbol_name'))
        assertion = sut.equals_list_resolver_element(symbol_reference_element)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, string_element)

    def test_string_not_equals_string_with_different_value(self):
        # ARRANGE #
        expected = lr.StringResolverElement(sr.string_constant('expected value'))
        actual = lr.StringResolverElement(sr.string_constant('actual value'))
        assertion = sut.equals_list_resolver_element(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_symbol_ref_not_equals_symbol_ref_with_different_symbol_name(self):
        # ARRANGE #
        expected = lr.SymbolReferenceElement(symbol_reference('expected_symbol_name'))
        actual = lr.SymbolReferenceElement(symbol_reference('actual_symbol_name'))
        assertion = sut.equals_list_resolver_element(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)


class TestEqualsResolver(unittest.TestCase):
    def test_equals(self):
        cases = [
            lr.ListResolver([lr.StringResolverElement(sr.string_constant('value'))]),
            lr.ListResolver([lr.SymbolReferenceElement(symbol_reference('symbol_name'))]),
        ]
        for resolver in cases:
            with self.subTest(msg=str(resolver)):
                sut.equals_list_resolver(resolver).apply_without_message(self, resolver)

    def test_not_equals(self):
        string_symbol = NameAndValue('string_symbol_name', 'string symbol value')
        cases = [
            Case('different number of elements',
                 expected=
                 lr.ListResolver([]),
                 actual=
                 lr.ListResolver([lr.StringResolverElement(sr.string_constant('value'))]),
                 ),
            Case('different value of single string',
                 expected=
                 lr.ListResolver([lr.StringResolverElement(sr.string_constant('expected value'))]),
                 actual=
                 lr.ListResolver([lr.StringResolverElement(sr.string_constant('actual value'))]),
                 ),
            Case('different element types, but same resolved value',
                 expected=
                 lr.ListResolver([lr.StringResolverElement(sr.string_constant(string_symbol.value))]),
                 actual=
                 lr.ListResolver([lr.SymbolReferenceElement(su.symbol_reference(string_symbol.name))]),
                 symbols=
                 su.symbol_table_with_single_string_value(string_symbol.name, string_symbol.value),
                 ),
        ]
        for case in cases:
            with self.subTest(msg=case.name):
                assertion = sut.equals_list_resolver(case.expected, case.symbols)
                assert_that_assertion_fails(assertion, case.actual)


class Case:
    def __init__(self,
                 name: str,
                 expected: lr.ListResolver,
                 actual: lr.ListResolver,
                 symbols: SymbolTable = None):
        self.name = name
        self.expected = expected
        self.actual = actual
        self.symbols = symbols
