import unittest

from exactly_lib.symbol.data import string_sdv as sut
from exactly_lib.symbol.data.impl import string_sdv_impls as impl
from exactly_lib.symbol.data.restrictions.reference_restrictions import OrReferenceRestrictions, is_any_data_type
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.type_system.data import concrete_strings as csv
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils as su
from exactly_lib_test.symbol.data.test_resources.concrete_value_assertions import equals_string_fragments
from exactly_lib_test.symbol.data.test_resources.list_ import ListConstantSymbolContext
from exactly_lib_test.symbol.data.test_resources.path import ConstantSuffixPathDdvSymbolContext
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import DataTypeSymbolReference
from exactly_lib_test.symbol.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.data.test_resources.string_ddv_assertions import equals_string_fragment_ddv, \
    equals_string_ddv


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
        symbol_reference = DataTypeSymbolReference('the_symbol_name', is_any_data_type())
        fragment = impl.SymbolStringFragmentSdv(symbol_reference.reference)
        # ACT #
        actual = list(fragment.references)
        # ASSERT #
        assertion = asrt.matches_singleton_sequence(symbol_reference.reference_assertion)
        assertion.apply_without_message(self, actual)

    def test_string_constant_SHOULD_raise_exception(self):
        fragment = impl.SymbolStringFragmentSdv(
            su.symbol_reference('the_symbol_name'))
        with self.assertRaises(ValueError):
            fragment.string_constant

    def test_resolve_of_string_symbol_SHOULD_give_string_constant(self):
        # ARRANGE #
        symbol = StringConstantSymbolContext('the_symbol_name', 'the symbol value')
        symbol_reference = symbol.reference__any_data_type
        fragment = impl.SymbolStringFragmentSdv(symbol_reference)
        symbol_table = symbol.symbol_table
        # ACT #
        actual = fragment.resolve(symbol_table)
        # ASSERT #
        self.assertIsInstance(actual, csv.StringDdvFragmentDdv)
        assertion = equals_string_fragment_ddv(csv.ConstantFragmentDdv(symbol.str_value))
        assertion.apply_without_message(self, actual)

    def test_resolve_of_path_symbol_SHOULD_give_string_constant(self):
        # ARRANGE #
        symbol = ConstantSuffixPathDdvSymbolContext('the_symbol_name',
                                                    RelOptionType.REL_ACT, 'file-name')
        fragment = impl.SymbolStringFragmentSdv(symbol.reference__any_data_type)
        symbol_table = symbol.symbol_table
        # ACT #
        actual = fragment.resolve(symbol_table)
        # ASSERT #
        self.assertIsInstance(actual, csv.PathFragmentDdv)
        assertion = equals_string_fragment_ddv(csv.PathFragmentDdv(symbol.ddv))
        assertion.apply_without_message(self, actual)

    def test_resolve_of_list_symbol_SHOULD_give_list_value(self):
        # ARRANGE #
        string_value_1 = 'string value 1'
        string_value_2 = 'string value 2'
        list_symbol = ListConstantSymbolContext('the_symbol_name',
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
    def test_resolve(self):
        string_constant_1 = 'string constant 1'
        string_constant_2 = 'string constant 2'
        string_symbol = StringConstantSymbolContext('string_symbol_name', 'string symbol value')
        path_symbol = ConstantSuffixPathDdvSymbolContext('path_symbol_name',
                                                         RelOptionType.REL_ACT,
                                                         'file-name')
        list_symbol = ListConstantSymbolContext('list_symbol_name',
                                                ['list element 1', 'list element 2']
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
                        string_symbol.reference__any_data_type),)),
                string_symbol.symbol_table,
                csv.StringDdv((csv.ConstantFragmentDdv(string_symbol.str_value),)),
            ),
            (
                'single symbol fragment/symbol is a path',
                sut.StringSdv((
                    impl.SymbolStringFragmentSdv(
                        path_symbol.reference__any_data_type),)),
                path_symbol.symbol_table,
                csv.StringDdv((csv.PathFragmentDdv(path_symbol.ddv),)),
            ),
            (
                'single symbol fragment/symbol is a list',
                sut.StringSdv((
                    impl.SymbolStringFragmentSdv(list_symbol.reference__any_data_type),)
                ),
                list_symbol.symbol_table,
                csv.StringDdv((csv.ListFragmentDdv(list_symbol.ddv),)),
            ),
            (
                'multiple fragments of different types',
                sut.StringSdv((
                    impl.SymbolStringFragmentSdv(string_symbol.reference__any_data_type),
                    impl.ConstantStringFragmentSdv(string_constant_1),
                    impl.SymbolStringFragmentSdv(path_symbol.reference__any_data_type),
                    impl.SymbolStringFragmentSdv(list_symbol.reference__any_data_type),
                )),
                SymbolContext.symbol_table_of_contexts([
                    string_symbol,
                    path_symbol,
                    list_symbol,
                ]),
                csv.StringDdv((csv.ConstantFragmentDdv(string_symbol.str_value),
                               csv.ConstantFragmentDdv(string_constant_1),
                               csv.PathFragmentDdv(path_symbol.ddv),
                               csv.ListFragmentDdv(list_symbol.ddv),
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
        reference_1 = DataTypeSymbolReference('symbol_1_name', is_any_data_type())
        reference_2 = DataTypeSymbolReference('symbol_2_name', OrReferenceRestrictions([]))
        cases = [
            (
                'no fragments',
                sut.StringSdv(()),
                asrt.is_empty_sequence,
            ),
            (
                'single string constant fragment',
                sut.StringSdv((impl.ConstantStringFragmentSdv(' value'),)),
                asrt.is_empty_sequence,
            ),
            (
                'multiple fragments of different types',
                sut.StringSdv((
                    impl.SymbolStringFragmentSdv(reference_1.reference),
                    impl.ConstantStringFragmentSdv(string_constant_1),
                    impl.SymbolStringFragmentSdv(reference_2.reference),
                )),
                asrt.matches_sequence([
                    reference_1.reference_assertion,
                    reference_2.reference_assertion,
                ]),
            ),
        ]
        for test_name, string_sdv, expected_references_assertion in cases:
            with self.subTest(test_name=test_name):
                actual = string_sdv.references
                expected_references_assertion.apply_without_message(self, actual)

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
