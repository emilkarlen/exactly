import unittest

from exactly_lib.symbol.data import string_sdv as sut
from exactly_lib.symbol.data.impl import string_sdv_impls as impl
from exactly_lib.symbol.data.restrictions.reference_restrictions import OrReferenceRestrictions
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_system.data import concrete_strings as csv
from exactly_lib.type_system.data import paths
from exactly_lib.type_system.data.concrete_strings import string_ddv_of_single_string
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib.type_system.value_type import DataValueType, TypeCategory, ValueType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import empty_symbol_table, Entry
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils as su
from exactly_lib_test.symbol.data.test_resources.concrete_value_assertions import equals_string_fragments
from exactly_lib_test.symbol.data.test_resources.list_ import ConstantListSymbolContext
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.type_system.data.test_resources.string_ddv_assertions import equals_string_fragment_ddv, \
    equals_string_ddv
from exactly_lib_test.util.test_resources import symbol_tables


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestConstantStringFragmentResolver),
        unittest.makeSuite(TestSymbolStringFragmentResolver),
        unittest.makeSuite(StringResolverTest),
    ])


class TestConstantStringFragmentResolver(unittest.TestCase):
    string_constant = 'string constant'
    fragment = impl.ConstantStringFragmentSdv(string_constant)

    def test_should_be_string_constant(self):
        self.assertTrue(self.fragment.is_string_constant)

    def test_should_have_no_references(self):
        self.assertEqual((),
                         self.fragment.references)

    def test_string_constant(self):
        string_constant = 'string constant'
        fragment = impl.ConstantStringFragmentSdv(string_constant)
        self.assertEqual(string_constant,
                         fragment.string_constant)

    def test_resolve_should_give_string_constant(self):
        # ARRANGE #
        string_constant = 'string constant'
        fragment = impl.ConstantStringFragmentSdv(string_constant)
        # ACT #
        actual = fragment.resolve(empty_symbol_table())
        # ASSERT #
        assertion = equals_string_fragment_ddv(csv.ConstantFragmentDdv(string_constant))
        assertion.apply_without_message(self, actual)


class TestSymbolStringFragmentResolver(unittest.TestCase):
    def test_should_be_string_constant(self):
        fragment = impl.SymbolStringFragmentSdv(
            su.symbol_reference('the_symbol_name'))
        self.assertFalse(fragment.is_string_constant)

    def test_should_have_exactly_one_references(self):
        # ARRANGE #
        symbol_reference = su.symbol_reference('the_symbol_name')
        fragment = impl.SymbolStringFragmentSdv(symbol_reference)
        # ACT #
        actual = list(fragment.references)
        # ASSERT #
        assertion = equals_symbol_references([symbol_reference])
        assertion.apply_without_message(self, actual)

    def test_string_constant_SHOULD_raise_exception(self):
        fragment = impl.SymbolStringFragmentSdv(
            su.symbol_reference('the_symbol_name'))
        with self.assertRaises(ValueError):
            fragment.string_constant

    def test_resolve_of_string_symbol_SHOULD_give_string_constant(self):
        # ARRANGE #
        symbol = NameAndValue('the_symbol_name', 'the symbol value')
        symbol_reference = su.symbol_reference(symbol.name)
        fragment = impl.SymbolStringFragmentSdv(symbol_reference)
        symbol_table = su.symbol_table_with_single_string_value(symbol.name, symbol.value)
        # ACT #
        actual = fragment.resolve(symbol_table)
        # ASSERT #
        self.assertIsInstance(actual, csv.StringDdvFragmentDdv)
        assertion = equals_string_fragment_ddv(csv.ConstantFragmentDdv(symbol.value))
        assertion.apply_without_message(self, actual)

    def test_resolve_of_path_symbol_SHOULD_give_string_constant(self):
        # ARRANGE #
        symbol = NameAndValue('the_symbol_name',
                              paths.rel_act(paths.constant_path_part('file-name')))
        symbol_reference = su.symbol_reference(symbol.name)
        fragment = impl.SymbolStringFragmentSdv(symbol_reference)
        symbol_table = su.symbol_table_with_single_path_value(symbol.name, symbol.value)
        # ACT #
        actual = fragment.resolve(symbol_table)
        # ASSERT #
        self.assertIsInstance(actual, csv.PathFragmentDdv)
        assertion = equals_string_fragment_ddv(csv.PathFragmentDdv(symbol.value))
        assertion.apply_without_message(self, actual)

    def test_resolve_of_list_symbol_SHOULD_give_list_value(self):
        # ARRANGE #
        string_value_1 = 'string value 1'
        string_value_2 = 'string value 2'
        list_symbol = ConstantListSymbolContext('the_symbol_name',
                                                [string_value_1, string_value_2]
                                                )
        symbol_reference = su.symbol_reference(list_symbol.name)
        fragment = impl.SymbolStringFragmentSdv(symbol_reference)

        symbol_table = list_symbol.symbol_table
        # ACT #
        actual = fragment.resolve(symbol_table)
        # ASSERT #
        self.assertIsInstance(actual, csv.ListFragmentDdv)
        assertion = equals_string_fragment_ddv(csv.ListFragmentDdv(list_symbol.ddv))
        assertion.apply_without_message(self, actual)


class StringResolverTest(unittest.TestCase):
    def test_value_type(self):
        # ARRANGE #
        sdv = sdv_with_single_constant_fragment('value')
        # ACT & ASSERT #
        self.assertIs(TypeCategory.DATA,
                      sdv.type_category)
        self.assertIs(DataValueType.STRING,
                      sdv.data_value_type)
        self.assertIs(ValueType.STRING,
                      sdv.value_type)

    def test_resolve(self):
        string_constant_1 = 'string constant 1'
        string_constant_2 = 'string constant 2'
        string_symbol = NameAndValue('string_symbol_name', 'string symbol value')
        path_symbol = NameAndValue('path_symbol_name',
                                   paths.rel_act(paths.constant_path_part('file-name')))
        list_element_1 = 'list element 1'
        list_element_2 = 'list element 2'
        list_symbol = NameAndValue('list_symbol_name',
                                   ListDdv([string_ddv_of_single_string(list_element_1),
                                            string_ddv_of_single_string(list_element_2)])
                                   )

        cases = [
            (
                'no fragments',
                sut.StringSdv(()),
                empty_symbol_table(),
                csv.StringDdv(()),
            ),
            (
                'single string constant fragment',
                sut.StringSdv((impl.ConstantStringFragmentSdv(string_constant_1),)),
                empty_symbol_table(),
                csv.StringDdv((csv.ConstantFragmentDdv(string_constant_1),)),
            ),
            (
                'multiple single string constant fragments',
                sut.StringSdv((impl.ConstantStringFragmentSdv(string_constant_1),
                               impl.ConstantStringFragmentSdv(string_constant_2))),
                empty_symbol_table(),
                csv.StringDdv((csv.ConstantFragmentDdv(string_constant_1),
                               csv.ConstantFragmentDdv(string_constant_2))),
            ),
            (
                'single symbol fragment/symbol is a string',
                sut.StringSdv((
                    impl.SymbolStringFragmentSdv(
                        su.symbol_reference(string_symbol.name)),)),
                su.symbol_table_with_single_string_value(string_symbol.name,
                                                         string_symbol.value),
                csv.StringDdv((csv.ConstantFragmentDdv(string_symbol.value),)),
            ),
            (
                'single symbol fragment/symbol is a path',
                sut.StringSdv((
                    impl.SymbolStringFragmentSdv(
                        su.symbol_reference(path_symbol.name)),)),
                su.symbol_table_with_single_path_value(path_symbol.name, path_symbol.value),
                csv.StringDdv((csv.PathFragmentDdv(path_symbol.value),)),
            ),
            (
                'single symbol fragment/symbol is a list',
                sut.StringSdv((
                    impl.SymbolStringFragmentSdv(
                        su.symbol_reference(list_symbol.name)),)),
                symbol_tables.symbol_table_from_entries([Entry(list_symbol.name,
                                                               su.list_ddv_constant_container(
                                                                   list_symbol.value))]),
                csv.StringDdv((csv.ListFragmentDdv(list_symbol.value),)),
            ),
            (
                'multiple fragments of different types',
                sut.StringSdv((
                    impl.SymbolStringFragmentSdv(su.symbol_reference(string_symbol.name)),
                    impl.ConstantStringFragmentSdv(string_constant_1),
                    impl.SymbolStringFragmentSdv(su.symbol_reference(path_symbol.name)),
                    impl.SymbolStringFragmentSdv(su.symbol_reference(list_symbol.name)),
                )),
                symbol_tables.symbol_table_from_entries([
                    Entry(string_symbol.name, su.string_constant_container(string_symbol.value)),
                    Entry(path_symbol.name, su.path_constant_container(path_symbol.value)),
                    Entry(list_symbol.name, su.list_ddv_constant_container(list_symbol.value)),
                ]),
                csv.StringDdv((csv.ConstantFragmentDdv(string_symbol.value),
                               csv.ConstantFragmentDdv(string_constant_1),
                               csv.PathFragmentDdv(path_symbol.value),
                               csv.ListFragmentDdv(list_symbol.value),
                               )),
            ),
        ]
        for test_name, string_value, symbol_table, expected in cases:
            with self.subTest(test_name=test_name):
                actual = string_value.resolve(symbol_table)
                assertion = equals_string_ddv(expected)
                assertion.apply_without_message(self, actual)

    def test_references(self):
        string_constant_1 = 'string constant 1'
        reference_1 = su.symbol_reference('symbol_1_name')
        reference_2 = SymbolReference('symbol_2_name', OrReferenceRestrictions([]))
        cases = [
            (
                'no fragments',
                sut.StringSdv(()),
                [],
            ),
            (
                'single string constant fragment',
                sut.StringSdv((impl.ConstantStringFragmentSdv(' value'),)),
                [],
            ),
            (
                'multiple fragments of different types',
                sut.StringSdv((
                    impl.SymbolStringFragmentSdv(reference_1),
                    impl.ConstantStringFragmentSdv(string_constant_1),
                    impl.SymbolStringFragmentSdv(reference_2),
                )),
                [reference_1, reference_2],
            ),
        ]
        for test_name, string_sdv, expected in cases:
            with self.subTest(test_name=test_name):
                actual = string_sdv.references
                assertion = equals_symbol_references(expected)
                assertion.apply_without_message(self, actual)

    def test_fragments(self):
        # ARRANGE #
        fragment_1 = impl.ConstantStringFragmentSdv('fragment 1 value')
        fragment_2 = impl.SymbolStringFragmentSdv(su.symbol_reference('symbol_name'))
        sdv = sut.StringSdv((fragment_1, fragment_2))
        # ACT #
        actual = sdv.fragments
        # ASSERT #
        assertion = equals_string_fragments([fragment_1, fragment_2])
        assertion.apply_without_message(self, actual)


def sdv_with_single_constant_fragment(fragment_value: str) -> sut.StringSdv:
    return sut.StringSdv((impl.ConstantStringFragmentSdv(fragment_value),))
