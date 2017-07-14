import unittest

from exactly_lib.symbol import list_resolver as sut
from exactly_lib.symbol import string_resolver as sr
from exactly_lib.symbol.restrictions.concrete_restrictions import OrReferenceRestrictions
from exactly_lib.type_system_values import list_value as lv
from exactly_lib.type_system_values.concrete_string_values import string_value_of_single_string
from exactly_lib.type_system_values.value_type import ValueType
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.symbol.test_resources import symbol_utils as su
from exactly_lib_test.symbol.test_resources.concrete_value_assertions import equals_string_resolver
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system_values.test_resources.list_value import equals_list_value


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(ListResolverTest)


class ListResolverTest(unittest.TestCase):
    def test_value_type(self):
        # ARRANGE #
        resolver = sut.ListResolver([])
        # ACT #
        actual = resolver.value_type
        # ASSERT #
        self.assertIs(ValueType.LIST,
                      actual)

    def test_resolve(self):
        string_constant_1 = 'string constant 1'
        string_constant_2 = 'string constant 2'
        string_symbol = NameAndValue('string_symbol_name', 'string symbol value')
        cases = [
            (
                'no elements',
                sut.ListResolver([]),
                empty_symbol_table(),
                lv.ListValue([]),
            ),
            (
                'single constant element',
                sut.ListResolver([sr.string_constant(string_constant_1)]),
                empty_symbol_table(),
                lv.ListValue([string_value_of_single_string(string_constant_1)]),
            ),
            (
                'multiple constant elements',
                sut.ListResolver([sr.string_constant(string_constant_1),
                                  sr.string_constant(string_constant_2)]),
                empty_symbol_table(),
                lv.ListValue([string_value_of_single_string(string_constant_1),
                              string_value_of_single_string(string_constant_2)]),
            ),
            (
                'single symbol reference element',
                sut.ListResolver([sr.symbol_reference(su.symbol_reference(string_symbol.name))]),
                su.symbol_table_with_single_string_value(string_symbol.name,
                                                         string_symbol.value),
                lv.ListValue([string_value_of_single_string(string_symbol.value)]),
            ),
        ]
        for test_name, list_value, symbol_table, expected in cases:
            with self.subTest(test_name=test_name):
                actual = list_value.resolve(symbol_table)
                assertion = equals_list_value(expected)
                assertion.apply_without_message(self, actual)

    def test_references(self):
        reference_1 = su.symbol_reference('symbol_1_name')
        reference_2 = su.SymbolReference('symbol_2_name', OrReferenceRestrictions([]))
        cases = [
            (
                'no elements',
                sut.ListResolver([]),
                [],
            ),
            (
                'single string constant element',
                sut.ListResolver([sr.string_constant('string value')]),
                [],
            ),
            (
                'multiple elements with multiple references',
                sut.ListResolver([
                    sr.symbol_reference(reference_1),
                    sr.string_constant('constant value'),
                    sr.symbol_reference(reference_2),
                ]),
                [reference_1, reference_2],
            ),
        ]
        for test_name, list_resolver, expected in cases:
            with self.subTest(test_name=test_name):
                actual = list_resolver.references
                assertion = equals_symbol_references(expected)
                assertion.apply_without_message(self, actual)

    def test_elements(self):
        # ARRANGE #
        element_1 = sr.string_constant('constant value')
        element_2 = sr.symbol_reference(su.symbol_reference('symbol_name'))
        resolver = sut.ListResolver([element_1, element_2])
        # ACT #
        actual = resolver.elements
        # ASSERT #
        assertion = asrt.matches_sequence([equals_string_resolver(element_1),
                                           equals_string_resolver(element_2)])
        assertion.apply_without_message(self, actual)


def resolver_with_single_constant_fragment(element_value: str) -> sut.ListResolver:
    return sut.ListResolver([string_value_of_single_string(element_value)])
