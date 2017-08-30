import unittest

from exactly_lib.named_element.named_element_usage import NamedElementReference
from exactly_lib.named_element.symbol import string_resolver as sr, list_resolver as lr
from exactly_lib.named_element.symbol.restrictions.reference_restrictions import OrReferenceRestrictions, \
    ReferenceRestrictionsOnDirectAndIndirect, no_restrictions
from exactly_lib.named_element.symbol.restrictions.value_restrictions import AnySymbolTypeRestriction
from exactly_lib.named_element.symbol.string_resolver import string_constant
from exactly_lib.type_system_values.concrete_string_values import string_value_of_single_string
from exactly_lib.util.symbol_table import SymbolTable, singleton_symbol_table_2
from exactly_lib_test.named_element.symbol.test_resources import symbol_utils as su, list_assertions as sut
from exactly_lib_test.named_element.symbol.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.named_element.symbol.test_resources.symbol_utils import symbol_reference
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsElement),
        unittest.makeSuite(TestEqualsResolver),
        unittest.makeSuite(TestEqualsConstantList),
        unittest.makeSuite(TestMatchesResolver),
    ])


class TestEqualsConstantList(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            (
                lr.ListResolver([]),
                []
            ),
            (
                lr.ListResolver([lr.StringResolverElement(sr.string_constant('value 1')),
                                 lr.StringResolverElement(sr.string_constant('value 2'))]),
                ['value 1', 'value 2']
            ),
        ]
        for actual, expected in test_cases:
            with self.subTest(expected=repr(expected)):
                sut.equals_constant_list(expected).apply_without_message(self, actual)

    def test_not_equals(self):
        test_cases = [
            (
                lr.ListResolver([]),
                ['non empty']
            ),
            (
                lr.ListResolver([lr.StringResolverElement(sr.string_constant('value 1')),
                                 lr.StringResolverElement(sr.string_constant('value 2 actual'))]),
                ['value 1', 'value 2 expected']
            ),
        ]
        for actual, expected in test_cases:
            assertion = sut.equals_constant_list(expected)
            with self.subTest(expected=repr(expected)):
                assert_that_assertion_fails(assertion, actual)


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


class TestMatchesResolver(unittest.TestCase):
    def test_equals(self):
        string_symbol = NameAndValue('string_symbol_name', 'string symbol value')
        cases = [
            MatchesCase('empty list of fragments',
                        expected=
                        lr.ListValue([]),
                        expected_references=
                        asrt.is_empty_list,
                        actual=
                        lr.ListResolver([]),
                        ),
            MatchesCase('single fragment',
                        expected=
                        lr.ListValue([string_value_of_single_string('expected value')]),
                        expected_references=
                        asrt.is_empty_list,
                        actual=
                        lr.ListResolver([lr.StringResolverElement(sr.string_constant('expected value'))]),
                        ),
            MatchesCase('symbol reference',
                        expected=
                        lr.ListValue([string_value_of_single_string(string_symbol.value)]),
                        expected_references=
                        equals_symbol_references([NamedElementReference(string_symbol.name,
                                                                        no_restrictions())]),
                        actual=
                        lr.ListResolver([lr.StringResolverElement(sr.symbol_reference(
                            NamedElementReference(string_symbol.name,
                                                  no_restrictions()),
                        ))]),
                        symbols=
                        singleton_symbol_table_2(string_symbol.name,
                                                 su.container(string_constant(string_symbol.value))),
                        ),
        ]
        for case in cases:
            with self.subTest(msg=case.name):
                assertion = sut.matches_list_resolver(case.expected, case.expected_references, case.symbols)
                assertion.apply_without_message(self, case.actual)

    def test_not_equals(self):
        string_symbol = NameAndValue('string_symbol_name', 'string symbol value')
        cases = [
            MatchesCase('different number of elements',
                        expected=
                        lr.ListValue([]),
                        expected_references=
                        asrt.is_empty_list,
                        actual=
                        lr.ListResolver([lr.StringResolverElement(sr.string_constant('value'))]),
                        ),
            MatchesCase('different value of single string',
                        expected=
                        lr.ListValue([string_value_of_single_string('expected value')]),
                        expected_references=
                        asrt.is_empty_list,
                        actual=
                        lr.ListResolver([lr.StringResolverElement(sr.string_constant('actual value'))]),
                        ),
            MatchesCase('different references',
                        expected=
                        lr.ListValue([string_value_of_single_string(string_symbol.value)]),
                        expected_references=
                        equals_symbol_references([NamedElementReference(string_symbol.name,
                                                                        ReferenceRestrictionsOnDirectAndIndirect(
                                                                            AnySymbolTypeRestriction()))]),
                        actual=
                        lr.ListResolver([lr.StringResolverElement(sr.symbol_reference(
                            NamedElementReference(string_symbol.name,
                                                  OrReferenceRestrictions([])),
                        ))]),
                        symbols=
                        singleton_symbol_table_2(string_symbol.name,
                                                 su.container(string_constant(string_symbol.value))),
                        ),
        ]
        for case in cases:
            with self.subTest(msg=case.name):
                assertion = sut.matches_list_resolver(case.expected, case.expected_references, case.symbols)
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


class MatchesCase:
    def __init__(self,
                 name: str,
                 expected: lr.ListValue,
                 expected_references: asrt.ValueAssertion,
                 actual: lr.ListResolver,
                 symbols: SymbolTable = None):
        self.name = name
        self.expected = expected
        self.expected_references = expected_references
        self.actual = actual
        self.symbols = symbols
