import unittest

from exactly_lib.util import symbol_table as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestConstruction),
        unittest.makeSuite(TestUpdate),
        unittest.makeSuite(TestLookup),
    ])


class TestConstruction(unittest.TestCase):
    def test_empty_symbol_table(self):
        actual = sut.empty_symbol_table()
        self.assertFalse(actual.names_set,
                         'names set should be empty')

    def test_construction_from_dict(self):
        # ARRANGE #
        symbol = NameAndValue('the symbol name',
                              ASymbolTableValue('the symbol value'))
        # ACT #
        actual = sut.SymbolTable({symbol.name: symbol.value})
        # ASSERT #
        _assert_table_contains_single_value(self, actual, symbol)

    def test_singleton_symbol_table(self):
        # ARRANGE #
        symbol = NameAndValue('symbol name',
                              ASymbolTableValue('symbol value'))
        # ACT #
        actual = sut.singleton_symbol_table(sut.Entry(symbol.name,
                                                      symbol.value))
        # ASSERT #
        _assert_table_contains_single_value(self, actual, symbol)

    def test_symbol_table_from_none_or_value_SHOULD_give_empty_table_WHEN_argument_is_none(self):
        actual = sut.symbol_table_from_none_or_value(None)
        self.assertFalse(actual.names_set,
                         'names set should be empty')

    def test_symbol_table_from_none_or_value_SHOULD_give_given_table_WHEN_argument_is_not_none(self):
        # ARRANGE #
        symbol = NameAndValue('symbol name',
                              ASymbolTableValue('symbol value'))
        symbol_table = sut.singleton_symbol_table(sut.Entry(symbol.name,
                                                            symbol.value))
        # ACT #
        actual = sut.symbol_table_from_none_or_value(symbol_table)
        # ASSERT #
        _assert_table_contains_single_value(self, actual, symbol)


class TestUpdate(unittest.TestCase):
    def test_put(self):
        # ARRANGE #
        symbol = NameAndValue('the symbol name',
                              ASymbolTableValue('the symbol value'))
        table = sut.empty_symbol_table()
        # ACT #
        table.put(symbol.name, symbol.value)
        # ASSERT #
        _assert_table_contains_single_value(self, table, symbol)

    def test_put_SHOULD_replace_value_WHEN_key_already_is_in_table(self):
        # ARRANGE #
        symbol_name = 'the symbol name'
        symbol_value_1 = ASymbolTableValue('the symbol 1 value')
        symbol_value_2 = ASymbolTableValue('the symbol 2 value')
        table = sut.SymbolTable({symbol_name: symbol_value_1})
        # ACT #
        table.put(symbol_name, symbol_value_2)
        # ASSERT #
        _assert_table_contains_single_value(self, table,
                                            NameAndValue(symbol_name, symbol_value_2))

    def test_add(self):
        # ARRANGE #
        symbol = NameAndValue('the symbol name',
                              ASymbolTableValue('the symbol value'))
        table = sut.empty_symbol_table()
        # ACT #
        table.add(sut.Entry(symbol.name, symbol.value))
        # ASSERT #
        _assert_table_contains_single_value(self, table, symbol)

    def test_add_all(self):
        # ARRANGE #
        symbol_1 = NameAndValue('the symbol 1 name',
                                ASymbolTableValue('the symbol 1 value'))
        symbol_2 = NameAndValue('the symbol 2 name',
                                ASymbolTableValue('the symbol 2 value'))
        table = sut.empty_symbol_table()
        # ACT #
        table.add_all([
            sut.Entry(symbol_1.name, symbol_1.value),
            sut.Entry(symbol_2.name, symbol_2.value),
        ])
        # ASSERT #
        _assert_table_contains(self, table, symbol_1)
        _assert_table_contains(self, table, symbol_2)
        self.assertEqual(2,
                         len(table.names_set))


class TestLookup(unittest.TestCase):
    def test_lookup_SHOULD_give_the_corresponding_value_WHEN_the_table_contains_the_given_key(self):
        # ARRANGE #
        symbol = NameAndValue('the symbol name',
                              ASymbolTableValue('the symbol value'))
        table = sut.SymbolTable({symbol.name: symbol.value})
        # ACT #
        actual = table.lookup(symbol.name)
        # ASSERT #
        self.assertIs(symbol.value,
                      actual)

    def test_lookup_SHOULD_raise_KeyError_WHEN_the_table_does_not_contains_the_given_key(self):
        # ARRANGE #
        table = sut.empty_symbol_table()
        # ACT #
        with self.assertRaises(KeyError):
            table.lookup('symbol_name')


def _assert_table_contains_single_value(put: unittest.TestCase,
                                        table: sut.SymbolTable,
                                        expected_symbol: NameAndValue):
    _assert_table_contains(put, table, expected_symbol)
    put.assertEqual({expected_symbol.name},
                    table.names_set,
                    'names set should contain a single value')


def _assert_table_contains(put: unittest.TestCase,
                           table: sut.SymbolTable,
                           expected_symbol: NameAndValue):
    put.assertTrue(table.contains(expected_symbol.name),
                   'table SHOULD contain the value')
    put.assertIn(expected_symbol.name,
                 table.names_set,
                 'names set should contain the value')
    put.assertIs(expected_symbol.value,
                 table.lookup(expected_symbol.name),
                 'lookup should fins the value')


class ASymbolTableValue(sut.SymbolTableValue):
    def __init__(self, value):
        self.value = value


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
