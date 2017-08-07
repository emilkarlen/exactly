import unittest

from exactly_lib.util.symbol_table import SymbolTable, empty_symbol_table
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.assert_that_assertion_fails import assert_that_assertion_fails
from exactly_lib_test.util.symbol_table import ASymbolTableValue
from exactly_lib_test.util.test_resources import symbol_table_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSymbolTableIsSingleton),
        unittest.makeSuite(TestSymbolTableKeysEquals),
    ])


class TestSymbolTableIsSingleton(unittest.TestCase):
    def test_succeed_WHEN_table_contains_the_expected_element(self):
        a_symbol = NameAndValue('symbol name',
                                ASymbolTableValue('symbol value'))
        cases = [
            ('assertion is',
             a_symbol,
             asrt.is_(a_symbol.value)
             ),
            ('assertion has expected value',
             a_symbol,
             assert_string_value_equals(a_symbol.value.value)
             ),
        ]
        for name, symbol, value_assertion in cases:
            with self.subTest(name=name):
                # ARRANGE #
                actual = SymbolTable({symbol.name: symbol.value})
                assertion = sut.assert_symbol_table_is_singleton(symbol.name, value_assertion)
                # ACT #
                assertion.apply_without_message(self, actual)

    def test_fail(self):
        a_symbol = NameAndValue('symbol name',
                                ASymbolTableValue('symbol value'))

        a_different_symbol = NameAndValue('a different symbol name',
                                          ASymbolTableValue('a different symbol value'))
        cases = [
            ('table is empty',
             empty_symbol_table(),
             a_symbol.name,
             asrt.anything_goes(),
             ),
            ('table is singleton but contains a different name',
             SymbolTable({a_symbol.name: a_symbol.value}),
             a_different_symbol.name,
             asrt.anything_goes(),
             ),
            ('table is singleton with given name but value assertion fails',
             SymbolTable({a_symbol.name: a_symbol.value}),
             a_symbol.name,
             assert_string_value_equals(a_different_symbol.value.value)
             ),
            ('table contains more than one element',
             SymbolTable({a_symbol.name: a_symbol.value,
                          a_different_symbol.name: a_different_symbol.value
                          }),
             a_symbol.name,
             asrt.anything_goes(),
             ),
        ]
        for name, table, symbol_name, value_assertion in cases:
            with self.subTest(name=name):
                assertion = sut.assert_symbol_table_is_singleton(symbol_name, value_assertion)
                assert_that_assertion_fails(assertion, table)


class TestSymbolTableKeysEquals(unittest.TestCase):
    def test_pass(self):
        a_symbol = NameAndValue('symbol name',
                                ASymbolTableValue('symbol value'))
        a_different_symbol = NameAndValue('a different symbol name',
                                          ASymbolTableValue('a different symbol value'))
        cases = [
            (
                'empty table',
                frozenset(),
                empty_symbol_table(),
            ),
            (
                'table with a single value',
                {a_symbol.name},
                SymbolTable({
                    a_symbol.name: a_symbol.value,
                }),
            ),
            (
                'table with a multiple values',
                {a_symbol.name,
                 a_different_symbol.name},
                SymbolTable({
                    a_symbol.name: a_symbol.value,
                    a_different_symbol.name: a_different_symbol.value,
                }),
            ),
        ]
        for name, expected_keys, actual_symbol_table in cases:
            with self.subTest(name=name):
                # ARRANGE #
                assertion = sut.assert_symbol_table_keys_equals(expected_keys)
                # ACT #
                assertion.apply_without_message(self, actual_symbol_table)

    def test_fail(self):
        a_symbol = NameAndValue('symbol name',
                                ASymbolTableValue('symbol value'))

        a_different_symbol = NameAndValue('a different symbol name',
                                          ASymbolTableValue('a different symbol value'))
        a_different_symbol_2 = NameAndValue('a different symbol name 2',
                                            ASymbolTableValue('a different symbol value 2'))
        cases = [
            (
                'expecting a single key but actual table is empty',
                {a_symbol.name},
                empty_symbol_table(),
            ),
            (
                'expecting empty set of keys but actual table is non-empty',
                frozenset(),
                SymbolTable({
                    a_symbol.name: a_symbol.value,
                }),
            ),
            (
                'number of keys is expected, but value is different',
                {a_symbol.name},
                SymbolTable({
                    a_different_symbol.name: a_different_symbol.value,
                }),
            ),
            (
                'number of keys is expected, but one of the keys is not expected',
                {a_symbol.name,
                 a_different_symbol.name},
                SymbolTable({
                    a_symbol.name: a_symbol.value,
                    a_different_symbol_2.name: a_different_symbol_2.value,
                }),
            ),
        ]
        for name, expected_keys, actual_symbol_table in cases:
            with self.subTest(name=name):
                # ARRANGE #
                assertion = sut.assert_symbol_table_keys_equals(expected_keys)
                # ACT #
                assert_that_assertion_fails(assertion, actual_symbol_table)


def assert_string_value_equals(expected_value: str) -> asrt.ValueAssertion:
    return asrt.sub_component('value',
                              ASymbolTableValue.value.fget,
                              asrt.equals(expected_value))
