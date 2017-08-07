import unittest

from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def assert_symbol_table_is_singleton(expected_name: str,
                                     value_assertion: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return _AssertSymbolTableIsSingleton(expected_name, value_assertion)


def assert_symbol_table_keys_equals(expected_keys: iter) -> asrt.ValueAssertion:
    return _AssertSymbolTableKeysEquals(expected_keys)


class _AssertSymbolTableIsSingleton(asrt.ValueAssertion):
    def __init__(self,
                 expected_name: str,
                 value_assertion: asrt.ValueAssertion):
        self.expected_name = expected_name
        self.value_assertion = value_assertion

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        assert isinstance(value, SymbolTable)
        put.assertEqual({self.expected_name},
                        value.names_set,
                        'Expecting a single entry')
        put.assertTrue(value.contains(self.expected_name),
                       'SymbolTable should contain the expected name')
        self.value_assertion.apply_with_message(put,
                                                value.lookup(self.expected_name),
                                                'value')


class _AssertSymbolTableKeysEquals(asrt.ValueAssertion):
    def __init__(self,
                 expected_keys: iter):
        self.expected_keys = expected_keys

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        assert isinstance(value, SymbolTable)
        put.assertEqual(frozenset(self.expected_keys),
                        value.names_set,
                        'keys are expected to match')
