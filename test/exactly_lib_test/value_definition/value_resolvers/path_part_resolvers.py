import unittest

from exactly_lib.test_case_file_structure.path_part import PathPart
from exactly_lib.util import symbol_table as st
from exactly_lib.value_definition.value_resolvers import path_part_resolvers as sut
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.value_definition.test_resources.concrete_restriction_assertion import is_string_value_restriction
from exactly_lib_test.value_definition.test_resources.value_definition_utils import string_value_container
from exactly_lib_test.value_definition.test_resources.value_reference_assertions import equals_value_reference


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestPathPartAsFixedPath),
        unittest.makeSuite(TestPathPartAsStringSymbolReference),
    ])


class TestPathPartAsFixedPath(unittest.TestCase):
    def test_value_references(self):
        # ARRANGE #
        path_part = sut.PathPartResolverAsFixedPath('the file name')
        # ACT #
        actual = path_part.references
        # ASSERT #
        self.assertEqual([],
                         actual,
                         'value references')

    def test_resolve(self):
        # ARRANGE #
        path_part = sut.PathPartResolverAsFixedPath('the file name')
        # ACT #
        symbols = st.empty_symbol_table()
        actual = path_part.resolve(symbols)
        # ASSERT #
        self.assertIsInstance(actual, PathPart)
        self.assertEqual('the file name',
                         actual.resolve(),
                         'resolved file name')


class TestPathPartAsStringSymbolReference(unittest.TestCase):
    def test_value_references(self):
        # ARRANGE #
        path_part = sut.PathPartResolverAsStringSymbolReference('the symbol name')
        # ACT #
        actual = path_part.references
        # ASSERT #
        assertion = asrt.matches_sequence([
            equals_value_reference('the symbol name',
                                   is_string_value_restriction)
        ])
        assertion.apply_with_message(self, actual, 'value references')

    def test_resolve(self):
        # ARRANGE #
        path_part = sut.PathPartResolverAsStringSymbolReference('the symbol name')
        symbol_table = st.singleton_symbol_table(st.Entry('the symbol name',
                                                          string_value_container('symbol value')))
        # ACT #
        actual = path_part.resolve(symbol_table)
        self.assertIsInstance(actual, PathPart)
        # ASSERT #
        self.assertEqual('symbol value',
                         actual.resolve(),
                         'resolved file name')
