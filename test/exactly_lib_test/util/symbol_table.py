import unittest
from typing import Sequence

from exactly_lib.util import symbol_table as sut
from exactly_lib.util.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestConstruction),
        unittest.makeSuite(TestUpdate),
        unittest.makeSuite(TestLookup),
        unittest.makeSuite(TestCopy),
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

    def test_symbol_table_from_none_or_value_SHOULD_give_empty_table_WHEN_argument_is_none(self):
        actual = sut.symbol_table_from_none_or_value(None)
        self.assertFalse(actual.names_set,
                         'names set should be empty')


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

    def test_add_table__empty_intersection(self):
        # ARRANGE #
        symbol_1 = NameAndValue('the symbol 1 name',
                                ASymbolTableValue('the symbol 1 value'))
        symbol_2 = NameAndValue('the symbol 2 name',
                                ASymbolTableValue('the symbol 2 value'))
        table1 = sut.SymbolTable({symbol_1.name: symbol_1.value})
        table2 = sut.SymbolTable({symbol_2.name: symbol_2.value})
        # ACT #
        table1.add_table(table2)
        # ASSERT #
        _assert_table_contains(self, table1, symbol_1)
        _assert_table_contains(self, table1, symbol_2)
        self.assertEqual(2,
                         len(table1.names_set))

    def test_add_table_SHOULD_replace_values_for_common_elements(self):
        # ARRANGE #
        name_of_common_symbol = 'the symbol 1 name'

        value1 = ASymbolTableValue('the symbol 1 value')
        value2 = ASymbolTableValue('the symbol 2 value')
        table1 = sut.SymbolTable({name_of_common_symbol: value1})
        table2 = sut.SymbolTable({name_of_common_symbol: value2})
        # ACT #
        table1.add_table(table2)
        # ASSERT #
        _assert_table_contains(self, table1, NameAndValue(name_of_common_symbol, value2))
        self.assertEqual(1,
                         len(table1.names_set))

    def test_add_table__intersecting_and_non_intersecting_elements(self):
        # ARRANGE #
        name_of_intersecting_symbol = 'the intersecting symbol name'

        symbol_1_ni = NameAndValue('symbol only in table 1 name',
                                   ASymbolTableValue('symbol only in table 1 value'))
        symbol_1_i = NameAndValue(name_of_intersecting_symbol,
                                  ASymbolTableValue(name_of_intersecting_symbol + ' value in table 1'))

        symbol_2_ni = NameAndValue('symbol only in table 2 name',
                                   ASymbolTableValue('symbol only in table 2 value'))
        symbol_2_i = NameAndValue(name_of_intersecting_symbol,
                                  ASymbolTableValue(name_of_intersecting_symbol + ' value in table 2'))

        table1 = _table_from_nav([symbol_1_i, symbol_1_ni])
        table2 = _table_from_nav([symbol_2_i, symbol_2_ni])
        # ACT #
        table1.add_table(table2)
        # ASSERT #
        _assert_table_contains(self, table1, symbol_1_ni)
        _assert_table_contains(self, table1, symbol_2_ni)
        _assert_table_contains(self, table1, symbol_2_i)
        self.assertEqual(3,
                         len(table1.names_set))


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


class TestCopy(unittest.TestCase):
    def test_WHEN_updating_a_copy_THEN_the_copy_SHOULD_be_updated_but_not_the_original(self):
        # ARRANGE #
        symbol = NameAndValue('the symbol name',
                              ASymbolTableValue('the symbol value'))
        original_table = sut.empty_symbol_table()
        # ACT #
        copied_table = original_table.copy()
        copied_table.put(symbol.name, symbol.value)
        # ASSERT #
        _assert_table_contains_single_value(self,
                                            copied_table,
                                            symbol)
        _assert_table_is_empty(self,
                               original_table)

    def test_WHEN_updating_a_copy_THEN_the_original_SHOULD_not_loose_elements(self):
        # ARRANGE #
        symbol_in_original = NameAndValue('the original symbol name',
                                          ASymbolTableValue('the original symbol value'))
        symbol_in_copy = NameAndValue('the copy symbol name',
                                      ASymbolTableValue('the copy symbol value'))
        original_table = sut.SymbolTable({symbol_in_original.name: symbol_in_original.value})
        # ACT #
        copied_table = original_table.copy()
        copied_table.put(symbol_in_copy.name, symbol_in_copy.value)
        # ASSERT #
        _assert_table_contains(self, copied_table, symbol_in_original)
        _assert_table_contains(self, copied_table, symbol_in_copy)
        self.assertEqual(2,
                         len(copied_table.names_set),
                         'the copy SHOULD contain the original symbol and the symbol added to the copy')
        _assert_table_contains_single_value(self,
                                            original_table,
                                            symbol_in_original)


class ASymbolTableValue(sut.SymbolTableValue):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value


def _assert_table_contains_single_value(put: unittest.TestCase,
                                        table: sut.SymbolTable,
                                        expected_symbol: NameAndValue[ASymbolTableValue]):
    _assert_table_contains(put, table, expected_symbol)
    put.assertEqual({expected_symbol.name},
                    table.names_set,
                    'names set should contain a single value')


def _assert_table_contains(put: unittest.TestCase,
                           table: sut.SymbolTable,
                           expected_symbol: NameAndValue[ASymbolTableValue]):
    put.assertTrue(table.contains(expected_symbol.name),
                   'table SHOULD contain the value')
    put.assertIn(expected_symbol.name,
                 table.names_set,
                 'names set should contain the value')
    put.assertIs(expected_symbol.value,
                 table.lookup(expected_symbol.name),
                 'lookup should fins the value')


def _assert_table_is_empty(put: unittest.TestCase,
                           table: sut.SymbolTable):
    put.assertEqual(frozenset(),
                    table.names_set,
                    'table SHOULD not contain any values')


def _table_from_nav(elements: Sequence[NameAndValue[ASymbolTableValue]]) -> sut.SymbolTable:
    return sut.SymbolTable({
        e.name: e.value
        for e in elements
    })


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
