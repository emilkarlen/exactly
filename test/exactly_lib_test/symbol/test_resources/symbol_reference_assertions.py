import unittest

from exactly_lib.symbol import value_structure as stc
from exactly_lib.symbol.value_structure import ReferenceRestrictions
from exactly_lib_test.symbol.test_resources.concrete_restriction_assertion import equals_value_restriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def matches_reference_restrictions(assertion_on_direct: asrt.ValueAssertion = asrt.anything_goes(),
                                   assertion_on_every: asrt.ValueAssertion = asrt.anything_goes(),
                                   ) -> asrt.ValueAssertion:
    return asrt.is_instance_with(ReferenceRestrictions,
                                 asrt.and_([
                                     asrt.sub_component('direct',
                                                        ReferenceRestrictions.direct.fget,
                                                        assertion_on_direct),
                                     asrt.sub_component('every',
                                                        ReferenceRestrictions.every.fget,
                                                        assertion_on_every)
                                 ])
                                 )


def equals_reference_restrictions(expected: ReferenceRestrictions) -> asrt.ValueAssertion:
    on_direct = equals_value_restriction(expected.direct)
    on_every = asrt.ValueIsNone()
    if expected.every is not None:
        on_every = equals_value_restriction(expected.every)
    return matches_reference_restrictions(assertion_on_direct=on_direct,
                                          assertion_on_every=on_every)


def matches_symbol_reference(expected_name: str,
                             assertion_on_restrictions: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return asrt.is_instance_with(
        stc.SymbolReference,
        asrt.and_([
            asrt.sub_component('name',
                               stc.SymbolReference.name.fget,
                               asrt.equals(expected_name)),
            asrt.sub_component('restrictions',
                               stc.SymbolReference.restrictions.fget,
                               assertion_on_restrictions)

        ]))


def equals_symbol_reference(expected_name: str,
                            assertion_on_direct_restriction: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return equals_symbol_reference2(expected_name,
                                    matches_reference_restrictions(assertion_on_direct=assertion_on_direct_restriction,
                                                                   assertion_on_every=asrt.ValueIsNone()))


def equals_symbol_reference2(expected_name: str,
                             assertion_on_restrictions: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return asrt.is_instance_with(
        stc.SymbolReference,
        asrt.and_([
            asrt.sub_component('name',
                               stc.SymbolReference.name.fget,
                               asrt.equals(expected_name)),
            asrt.sub_component('restrictions',
                               stc.SymbolReference.restrictions.fget,
                               assertion_on_restrictions)

        ]))


def equals_symbol_references(expected: list) -> asrt.ValueAssertion:
    return _EqualsValueReferences(expected)


class _EqualsValueReferences(asrt.ValueAssertion):
    def __init__(self, expected: list):
        self._expected = expected
        assert isinstance(expected, list), 'Value reference list must be a list'
        for idx, element in enumerate(expected):
            assert isinstance(element, stc.SymbolReference), 'Element must be a ValueReference #' + str(idx)

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value, list,
                             'Expects a list of value references')
        put.assertEqual(len(self._expected),
                        len(value),
                        message_builder.apply('Number of value references'))
        for idx, expected_ref in enumerate(self._expected):
            actual_ref = value[idx]
            put.assertIsInstance(actual_ref, stc.SymbolReference)
            assert isinstance(actual_ref, stc.SymbolReference)
            assert isinstance(expected_ref, stc.SymbolReference)
            expected_restrictions = expected_ref.restrictions
            element_assertion = equals_symbol_reference2(expected_ref.name,
                                                         equals_reference_restrictions(expected_restrictions))
            element_assertion.apply(put,
                                    actual_ref,
                                    message_builder.for_sub_component('[%d]' % idx))
