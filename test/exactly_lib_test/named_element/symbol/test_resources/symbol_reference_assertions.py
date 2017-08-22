import unittest

from exactly_lib.named_element import symbol_usage as su
from exactly_lib.named_element.symbol_usage import SymbolReference
from exactly_lib_test.named_element.symbol.restrictions.test_resources.concrete_restriction_assertion import \
    matches_restrictions_on_direct_and_indirect, equals_reference_restrictions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def matches_symbol_reference(expected_name: str,
                             assertion_on_restrictions: asrt.ValueAssertion = asrt.anything_goes()
                             ) -> asrt.ValueAssertion:
    return asrt.is_instance_with(
        su.SymbolReference,
        asrt.and_([
            asrt.sub_component('name',
                               su.SymbolReference.name.fget,
                               asrt.equals(expected_name)),
            asrt.sub_component('restrictions',
                               su.SymbolReference.restrictions.fget,
                               assertion_on_restrictions)

        ]))


def equals_symbol_reference_with_restriction_on_direct_target(expected_name: str,
                                                              assertion_on_direct_restriction: asrt.ValueAssertion
                                                              ) -> asrt.ValueAssertion:
    return matches_symbol_reference(expected_name,
                                    matches_restrictions_on_direct_and_indirect(
                                        assertion_on_direct=assertion_on_direct_restriction,
                                        assertion_on_every=asrt.ValueIsNone()))


def equals_symbol_reference(expected: SymbolReference) -> asrt.ValueAssertion:
    return matches_symbol_reference(expected.name,
                                    equals_reference_restrictions(expected.restrictions))


def equals_symbol_references(expected: list) -> asrt.ValueAssertion:
    return _EqualsSymbolReferences(expected)


class _EqualsSymbolReferences(asrt.ValueAssertion):
    def __init__(self, expected: list):
        self._expected = expected
        assert isinstance(expected, list), 'Symbol reference list must be a list'
        for idx, element in enumerate(expected):
            assert isinstance(element,
                              su.SymbolReference), 'Element must be a SymbolReference #' + str(idx)

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value, list,
                             'Expects a list of symbol references')
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
