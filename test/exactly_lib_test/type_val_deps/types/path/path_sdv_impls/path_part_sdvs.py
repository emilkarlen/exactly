import unittest

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.sym_ref.data.reference_restrictions import is_any_data_type
from exactly_lib.type_val_deps.types.path.path_part_ddv import PathPartDdv
from exactly_lib.type_val_deps.types.path.path_sdv_impls import path_part_sdvs as sut
from exactly_lib.type_val_deps.types.string import string_sdvs
from exactly_lib.util import symbol_table as st
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.symbol.test_resources.symbol_usage_assertions import matches_reference_2
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestPathPartAsFixedPath),
        unittest.makeSuite(TestPathPartResolverAsStringResolver),
    ])


class TestPathPartAsFixedPath(unittest.TestCase):
    def test_symbol_references(self):
        # ARRANGE #
        path_part = sut.PathPartSdvAsConstantPath('the file name')
        # ACT #
        actual = path_part.references
        # ASSERT #
        self.assertEqual([],
                         actual,
                         'symbol references')

    def test_resolve(self):
        # ARRANGE #
        path_part = sut.PathPartSdvAsConstantPath('the file name')
        # ACT #
        symbols = st.empty_symbol_table()
        actual = path_part.resolve(symbols)
        # ASSERT #
        self.assertIsInstance(actual, PathPartDdv)
        self.assertEqual('the file name',
                         actual.value(),
                         'resolved file name')


class TestPathPartResolverAsStringResolver(unittest.TestCase):
    def test_symbol_references(self):
        # ARRANGE #
        symbol1 = NameAndValue('symbol_1_name', 'symbol 1 value')
        symbol1_ref = self._symbol_reference(symbol1.name)
        symbol2 = NameAndValue('symbol_2_name', 'symbol 2 value')
        symbol2_ref = self._symbol_reference(symbol2.name)
        fragments = [string_sdvs.symbol_fragment(symbol1_ref),
                     string_sdvs.symbol_fragment(symbol2_ref)]
        sdv = sut.StringSdv(tuple(fragments))
        path_part = sut.PathPartSdvAsStringSdv(sdv)
        # ACT #
        actual = path_part.references
        # ASSERT #
        assertion = asrt.matches_sequence([
            matches_reference_2(symbol1.name),
            matches_reference_2(symbol2.name),
        ])
        assertion.apply_with_message(self, actual, 'symbol references')

    def test_resolve(self):
        # ARRANGE #
        symbol1 = StringConstantSymbolContext('symbol_1_name', 'symbol 1 value')
        symbol1_ref = self._symbol_reference(symbol1.name)
        symbol2 = StringConstantSymbolContext('symbol_2_name', 'symbol 2 value')
        symbol2_ref = self._symbol_reference(symbol2.name)
        fragments = [string_sdvs.symbol_fragment(symbol1_ref),
                     string_sdvs.symbol_fragment(symbol2_ref)]
        sdv = sut.StringSdv(tuple(fragments))
        path_part = sut.PathPartSdvAsStringSdv(sdv)
        symbol_table_entries = [symbol1, symbol2]
        symbol_table = SymbolContext.symbol_table_of_contexts(symbol_table_entries)
        # ACT #
        actual = path_part.resolve(symbol_table)
        self.assertIsInstance(actual, PathPartDdv)
        # ASSERT #
        expected_resolved_value = symbol1.str_value + symbol2.str_value
        self.assertEqual(expected_resolved_value,
                         actual.value(),
                         'resolved path part')

    @staticmethod
    def _symbol_reference(symbol_name: str) -> SymbolReference:
        return SymbolReference(symbol_name, is_any_data_type())
