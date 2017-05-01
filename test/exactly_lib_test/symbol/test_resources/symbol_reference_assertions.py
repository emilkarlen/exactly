import unittest

from exactly_lib.symbol import value_structure as stc
from exactly_lib_test.symbol.test_resources.concrete_restriction_assertion import equals_value_restriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_symbol_reference(expected_name: str,
                            value_restriction_assertion: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return asrt.is_instance_with(stc.SymbolReference,
                                 asrt.and_([
                                     asrt.sub_component('name',
                                                        stc.SymbolReference.name.fget,
                                                        asrt.equals(expected_name)),
                                     asrt.sub_component('value_restriction',
                                                        stc.SymbolReference.value_restriction.fget,
                                                        value_restriction_assertion)

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
            expected_value_restriction = expected_ref.value_restriction
            element_assertion = equals_symbol_reference(expected_ref.name,
                                                        equals_value_restriction(expected_value_restriction))
            element_assertion.apply(put,
                                    actual_ref,
                                    message_builder.for_sub_component('[%d]' % idx))
