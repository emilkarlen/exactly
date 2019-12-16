import unittest

from exactly_lib.symbol.data import list_sdv as sut
from exactly_lib.symbol.data import list_sdvs
from exactly_lib.symbol.data.restrictions.reference_restrictions import OrReferenceRestrictions
from exactly_lib.type_system.data.concrete_strings import string_ddv_of_single_string, \
    string_ddv_of_single_path
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib.type_system.value_type import DataValueType, TypeCategory, ValueType
from exactly_lib.util.symbol_table import empty_symbol_table, SymbolTable
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils as su
from exactly_lib_test.symbol.data.test_resources.list_assertions import equals_list_sdv_element
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_case_file_structure.test_resources.simple_path import path_test_impl
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.data.test_resources.list_ddv_assertions import equals_list_ddv


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(ListResolverTest)


class ListResolverTest(unittest.TestCase):
    def test_value_type(self):
        # ARRANGE #
        sdv = sut.ListSdv([])
        # ACT & ASSERT #
        self.assertIs(TypeCategory.DATA,
                      sdv.type_category)
        self.assertIs(DataValueType.LIST,
                      sdv.data_value_type)
        self.assertIs(ValueType.LIST,
                      sdv.value_type)

    def test_resolve_without_symbol_references(self):
        string_constant_1 = 'string constant 1'
        string_constant_2 = 'string constant 2'
        string_symbol = NameAndValue('string_symbol_name', 'string symbol value')
        cases = [
            Case(
                'no elements',
                sdv_to_check=
                sut.ListSdv([]),
                symbols=
                empty_symbol_table(),
                expected_resolved_value=
                ListDdv([]),
            ),
            Case(
                'single constant element',
                sdv_to_check=
                sut.ListSdv([list_sdvs.str_element(string_constant_1)]),
                symbols=
                empty_symbol_table(),
                expected_resolved_value=
                ListDdv([string_ddv_of_single_string(string_constant_1)]),
            ),
            Case(
                'multiple constant elements',
                sdv_to_check=
                sut.ListSdv([list_sdvs.str_element(string_constant_1),
                             list_sdvs.str_element(string_constant_2)]),
                symbols=
                empty_symbol_table(),
                expected_resolved_value=
                ListDdv([string_ddv_of_single_string(string_constant_1),
                         string_ddv_of_single_string(string_constant_2)]),
            ),
            Case(
                'single string symbol reference element',
                sdv_to_check=
                sut.ListSdv([list_sdvs.symbol_element(su.symbol_reference(string_symbol.name))]),
                symbols=
                su.symbol_table_with_single_string_value(string_symbol.name,
                                                         string_symbol.value),
                expected_resolved_value=
                ListDdv([string_ddv_of_single_string(string_symbol.value)]),
            ),
        ]
        self._check('resolve without symbol references', cases)

    def test_resolve_with_concatenation_of_referenced_list_symbols(self):
        empty_list_symbol = NameAndValue('empty_list_symbol', ListDdv([]))
        multi_element_list_symbol = NameAndValue('multi_element_list_symbol',
                                                 ListDdv([string_ddv_of_single_string('multi list element 1'),
                                                          string_ddv_of_single_string('multi list element 2')]))
        cases = [
            Case(
                'WHEN list is a single symbol reference AND symbol is an empty list '
                'THEN resolved value'
                'SHOULD be an empty list',
                sdv_to_check=
                sut.ListSdv([list_sdvs.symbol_element(su.symbol_reference(empty_list_symbol.name))]),
                symbols=
                su.symbol_table_with_single_list_value(empty_list_symbol.name,
                                                       empty_list_symbol.value),
                expected_resolved_value=
                empty_list_symbol.value,
            ),
            Case(
                'WHEN list is a single symbol reference AND symbol is a non-empty list '
                'THEN resolved value'
                'SHOULD be equal to the non-empty list',
                sdv_to_check=
                sut.ListSdv([list_sdvs.symbol_element(su.symbol_reference(multi_element_list_symbol.name))]),
                symbols=
                su.symbol_table_with_single_list_value(multi_element_list_symbol.name,
                                                       multi_element_list_symbol.value),
                expected_resolved_value=
                multi_element_list_symbol.value,
            ),
            Case(
                'WHEN list is multiple symbol reference AND all symbols are lists'
                'THEN resolved value'
                'SHOULD be equal to the concatenation of referenced lists',
                sdv_to_check=
                sut.ListSdv([list_sdvs.symbol_element(su.symbol_reference(multi_element_list_symbol.name)),
                             list_sdvs.symbol_element(su.symbol_reference(empty_list_symbol.name)),
                             list_sdvs.symbol_element(su.symbol_reference(multi_element_list_symbol.name))]),
                symbols=
                su.symbol_table_from_symbol_definitions([
                    su.list_symbol_definition(multi_element_list_symbol.name,
                                              multi_element_list_symbol.value),
                    su.list_symbol_definition(empty_list_symbol.name,
                                              empty_list_symbol.value),
                ]),
                expected_resolved_value=
                ListDdv(list(multi_element_list_symbol.value.string_elements +
                             multi_element_list_symbol.value.string_elements)),
            ),
        ]
        self._check('concatenation of referenced list symbols', cases)

    def test_reference_to_symbol_that_are_not_lists(self):
        string_symbol_str = 'string constant'
        string_symbol = NameAndValue('string_symbol',
                                     string_ddv_of_single_string(string_symbol_str))
        path_symbol = NameAndValue('path_symbol',
                                   path_test_impl())
        cases = [
            Case(
                'reference to string symbol',
                sdv_to_check=
                sut.ListSdv([list_sdvs.symbol_element(su.symbol_reference(string_symbol.name))]),
                symbols=
                su.symbol_table_from_symbol_definitions([
                    su.string_ddv_symbol_definition(string_symbol.name,
                                                    string_symbol.value)]),
                expected_resolved_value=
                ListDdv([string_symbol.value]),
            ),
            Case(
                'reference to path symbol '
                'SHOULD resolve to string representation of the path value',
                sdv_to_check=
                sut.ListSdv([list_sdvs.symbol_element(su.symbol_reference(path_symbol.name))]),
                symbols=
                su.symbol_table_from_symbol_definitions([
                    su.path_symbol_definition(path_symbol.name,
                                              path_symbol.value)]),
                expected_resolved_value=
                ListDdv([string_ddv_of_single_path(path_symbol.value)]),
            ),
            Case(
                'combination of string and path value',
                sdv_to_check=
                sut.ListSdv([list_sdvs.symbol_element(su.symbol_reference(string_symbol.name)),
                             list_sdvs.symbol_element(su.symbol_reference(path_symbol.name))]),
                symbols=
                su.symbol_table_from_symbol_definitions([
                    su.string_ddv_symbol_definition(string_symbol.name,
                                                    string_symbol.value),
                    su.path_symbol_definition(path_symbol.name,
                                              path_symbol.value),
                ]),
                expected_resolved_value=
                ListDdv([string_symbol.value,
                         string_ddv_of_single_path(path_symbol.value)]),
            ),
        ]
        self._check('reference to symbol that are not lists', cases)

    def _check(self, suite_name: str, cases: list):
        for case in cases:
            with self.subTest(suite_name=suite_name, test_name=case.case_name):
                actual = case.sdv_to_check.resolve(case.symbols)
                assertion = equals_list_ddv(case.expected_resolved_value)
                assertion.apply_without_message(self, actual)

    def test_references(self):
        reference_1 = su.symbol_reference('symbol_1_name')
        reference_2 = su.SymbolReference('symbol_2_name', OrReferenceRestrictions([]))
        cases = [
            (
                'no elements',
                sut.ListSdv([]),
                [],
            ),
            (
                'single string constant element',
                sut.ListSdv([list_sdvs.str_element('string value')]),
                [],
            ),
            (
                'multiple elements with multiple references',
                sut.ListSdv([
                    list_sdvs.symbol_element(reference_1),
                    list_sdvs.str_element('constant value'),
                    list_sdvs.symbol_element(reference_2),
                ]),
                [reference_1, reference_2],
            ),
        ]
        for test_name, list_sdv, expected in cases:
            with self.subTest(test_name=test_name):
                actual = list_sdv.references
                assertion = equals_symbol_references(expected)
                assertion.apply_without_message(self, actual)

    def test_elements(self):
        # ARRANGE #
        element_1 = list_sdvs.str_element('constant value')
        element_2 = list_sdvs.symbol_element(su.symbol_reference('symbol_name'))
        sdv = sut.ListSdv([element_1, element_2])
        # ACT #
        actual = sdv.elements
        # ASSERT #
        assertion = asrt.matches_sequence([equals_list_sdv_element(element_1),
                                           equals_list_sdv_element(element_2)])
        assertion.apply_without_message(self, actual)


def sdv_with_single_constant_fragment(element_value: str) -> sut.ListSdv:
    return sut.ListSdv([string_ddv_of_single_string(element_value)])


class Case:
    def __init__(self,
                 case_name: str,
                 sdv_to_check: sut.ListSdv,
                 symbols: SymbolTable,
                 expected_resolved_value: sut.ListDdv):
        self.expected_resolved_value = expected_resolved_value
        self.symbols = symbols
        self.sdv_to_check = sdv_to_check
        self.case_name = case_name