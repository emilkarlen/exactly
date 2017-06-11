import unittest

from exactly_lib.symbol.value_resolvers import string_resolvers as sut
from exactly_lib.symbol.value_structure import ValueType
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.symbol.test_resources.concrete_value_assertions import equals_string_fragments


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(StringConstant)


class StringConstant(unittest.TestCase):
    def test_value_type(self):
        # ARRANGE #
        resolver = sut.StringConstant('value')
        # ACT #
        actual = resolver.value_type
        # ASSERT #
        self.assertIs(ValueType.STRING,
                      actual)

    def test_resolved_value(self):
        # ARRANGE #
        string_value = 'value'
        resolver = sut.StringConstant(string_value)
        # ACT #
        actual = resolver.resolve(empty_symbol_table())
        # ASSERT #
        self.assertEquals(string_value,
                          actual)

    def test_fragments(self):
        # ARRANGE #
        resolver = sut.StringConstant('value')
        # ACT #
        actual = resolver.fragments
        # ASSERT #
        equals_string_fragments(()).apply_without_message(self, actual)
