import unittest
from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    matches_restrictions_on_direct_and_indirect, equals_data_type_reference_restrictions, \
    is_any_data_type_reference_restrictions
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restrictions import \
    string_made_up_of_just_strings_reference_restrictions
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_type_category_restriction
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import matches_reference_2
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase


def equals_symbol_reference_with_restriction_on_direct_target(expected_name: str,
                                                              assertion_on_direct_restriction: ValueAssertion
                                                              ) -> ValueAssertion[SymbolReference]:
    return asrt_sym_ref.matches_reference_2(expected_name,
                                            matches_restrictions_on_direct_and_indirect(
                                                assertion_on_direct=assertion_on_direct_restriction,
                                                assertion_on_every=asrt.ValueIsNone()))


def equals_symbol_reference(expected: SymbolReference) -> ValueAssertion[SymbolReference]:
    return asrt_sym_ref.matches_reference_2(expected.name,
                                            equals_data_type_reference_restrictions(expected.restrictions))


def symbol_usage_equals_symbol_reference(expected: SymbolReference) -> ValueAssertion[SymbolUsage]:
    return asrt.is_instance_with(
        SymbolUsage,
        asrt_sym_ref.matches_reference_2(
            expected.name,
            equals_data_type_reference_restrictions(expected.restrictions)))


def is_reference_to_data_category_symbol(symbol_name: str) -> ValueAssertion[SymbolReference]:
    return asrt_sym_ref.matches_reference_2(symbol_name,
                                            is_type_category_restriction(TypeCategory.DATA))


def equals_symbol_references(expected: Sequence[SymbolReference]) -> ValueAssertion[Sequence[SymbolReference]]:
    return _EqualsSymbolReferences(expected)


class _EqualsSymbolReferences(ValueAssertionBase):
    def __init__(self, expected: Sequence[SymbolReference]):
        self._expected = expected
        assert isinstance(expected, Sequence), 'Symbol reference list must be a Sequence'
        for idx, element in enumerate(expected):
            assert isinstance(element,
                              SymbolReference), 'Element must be a SymbolReference #' + str(idx)

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, Sequence,
                             'Expects a Sequence of symbol references')
        put.assertEqual(len(self._expected),
                        len(value),
                        message_builder.apply('Number of symbol references'))
        for idx, expected_ref in enumerate(self._expected):
            actual_ref = value[idx]
            put.assertIsInstance(actual_ref, SymbolReference)
            assert isinstance(actual_ref, SymbolReference)
            assert isinstance(expected_ref, SymbolReference)
            element_assertion = equals_symbol_reference(expected_ref)
            element_assertion.apply(put,
                                    actual_ref,
                                    message_builder.for_sub_component('[%d]' % idx))


def is_reference_to_data_type_symbol(symbol_name: str
                                     ) -> ValueAssertion[SymbolReference]:
    return matches_reference_2(symbol_name,
                               is_any_data_type_reference_restrictions())


def is_reference_to_string_made_up_of_just_plain_strings(symbol_name: str) -> ValueAssertion[SymbolReference]:
    return equals_symbol_reference(
        SymbolReference(symbol_name,
                        string_made_up_of_just_strings_reference_restrictions()))
