import unittest
from typing import Sequence

from exactly_lib.symbol import symbol_usage as su
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    matches_restrictions_on_direct_and_indirect, equals_data_type_reference_restrictions
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_type_category_restriction
from exactly_lib_test.symbol.test_resources.symbol_usage_assertions import matches_reference_2
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_symbol_reference_with_restriction_on_direct_target(expected_name: str,
                                                              assertion_on_direct_restriction: asrt.ValueAssertion
                                                              ) -> asrt.ValueAssertion:
    return matches_reference_2(expected_name,
                               matches_restrictions_on_direct_and_indirect(
                                   assertion_on_direct=assertion_on_direct_restriction,
                                   assertion_on_every=asrt.ValueIsNone()))


def equals_symbol_reference(expected: SymbolReference) -> asrt.ValueAssertion[SymbolReference]:
    return matches_reference_2(expected.name,
                               equals_data_type_reference_restrictions(expected.restrictions))


def is_reference_to_data_category_symbol(symbol_name: str) -> asrt.ValueAssertion[SymbolReference]:
    return matches_reference_2(symbol_name,
                               is_type_category_restriction(TypeCategory.DATA))


def equals_symbol_references(expected: Sequence[SymbolReference]) -> asrt.ValueAssertion[Sequence[SymbolReference]]:
    return _EqualsSymbolReferences(expected)


class _EqualsSymbolReferences(asrt.ValueAssertion):
    def __init__(self, expected: Sequence[SymbolReference]):
        self._expected = expected
        assert isinstance(expected, Sequence), 'Symbol reference list must be a Sequence'
        for idx, element in enumerate(expected):
            assert isinstance(element,
                              su.SymbolReference), 'Element must be a SymbolReference #' + str(idx)

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value, Sequence,
                             'Expects a Sequence of symbol references')
        put.assertEqual(len(self._expected),
                        len(value),
                        message_builder.apply('Number of symbol references'))
        for idx, expected_ref in enumerate(self._expected):
            actual_ref = value[idx]
            put.assertIsInstance(actual_ref, su.SymbolReference)
            assert isinstance(actual_ref, su.SymbolReference)
            assert isinstance(expected_ref, su.SymbolReference)
            element_assertion = equals_symbol_reference(expected_ref)
            element_assertion.apply(put,
                                    actual_ref,
                                    message_builder.for_sub_component('[%d]' % idx))
