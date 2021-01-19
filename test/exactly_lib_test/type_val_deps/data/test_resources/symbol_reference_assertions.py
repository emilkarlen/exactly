from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference
from exactly_lib.symbol.value_type import TypeCategory
from exactly_lib.type_val_deps.sym_ref.data.data_value_restriction import ValueRestriction
from exactly_lib.type_val_deps.sym_ref.restrictions import DataTypeReferenceRestrictions
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import matches_reference_2
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.data.test_resources import concrete_restriction_assertion
from exactly_lib_test.type_val_deps.data.test_resources.concrete_restriction_assertion import \
    matches_restrictions_on_direct_and_indirect, equals_data_type_reference_restrictions, \
    is_any_data_type_reference_restrictions
from exactly_lib_test.type_val_deps.sym_ref.test_resources.restrictions_assertions import is_type_category_restriction


def matches_symbol_reference_with_restriction_on_direct_target(
        expected_name: str,
        assertion_on_direct_restriction: ValueAssertion[ValueRestriction]
) -> ValueAssertion[SymbolReference]:
    return asrt_sym_ref.matches_reference_2(expected_name,
                                            matches_restrictions_on_direct_and_indirect(
                                                assertion_on_direct=assertion_on_direct_restriction,
                                                assertion_on_every=asrt.ValueIsNone()))


def equals_data_type_symbol_reference(expected: SymbolReference) -> ValueAssertion[SymbolReference]:
    restrictions = expected.restrictions
    if not isinstance(restrictions, DataTypeReferenceRestrictions):
        raise ValueError('Restrictions must be {}. Found {}'.format(
            DataTypeReferenceRestrictions,
            restrictions,
        ))
    return asrt_sym_ref.matches_reference_2(expected.name,
                                            equals_data_type_reference_restrictions(restrictions))


def matches_data_type_symbol_reference(symbol_name: str,
                                       restrictions: DataTypeReferenceRestrictions) -> ValueAssertion[SymbolReference]:
    return asrt_sym_ref.matches_reference_2(symbol_name,
                                            equals_data_type_reference_restrictions(restrictions))


class DataTypeSymbolReference:
    def __init__(self,
                 name: str,
                 restrictions: DataTypeReferenceRestrictions,
                 ):
        self.name = name
        self.restrictions = restrictions

    @property
    def reference(self) -> SymbolReference:
        return SymbolReference(self.name, self.restrictions)

    @property
    def reference_assertion(self) -> ValueAssertion[SymbolReference]:
        return matches_data_type_symbol_reference(self.name, self.restrictions)


def symbol_usage_equals_data_type_symbol_reference(expected: SymbolReference) -> ValueAssertion[SymbolUsage]:
    restrictions = expected.restrictions
    if not isinstance(restrictions, DataTypeReferenceRestrictions):
        raise ValueError('Restrictions must be {}. Found {}'.format(
            DataTypeReferenceRestrictions,
            restrictions,
        ))
    return asrt.is_instance_with(
        SymbolUsage,
        asrt_sym_ref.matches_reference_2(
            expected.name,
            equals_data_type_reference_restrictions(restrictions)))


def is_reference_to_data_category_symbol(symbol_name: str) -> ValueAssertion[SymbolReference]:
    return asrt_sym_ref.matches_reference_2(symbol_name,
                                            is_type_category_restriction(TypeCategory.DATA))


def equals_data_type_symbol_references(expected: Sequence[SymbolReference]
                                       ) -> ValueAssertion[Sequence[SymbolReference]]:
    return asrt.matches_sequence([
        equals_data_type_symbol_reference(expected_ref)
        for expected_ref in expected
    ])


def is_reference_to_data_type_symbol(symbol_name: str
                                     ) -> ValueAssertion[SymbolReference]:
    return matches_reference_2(symbol_name,
                               is_any_data_type_reference_restrictions())


def is_reference_restrictions__to_type_convertible_to_string(symbol_name: str
                                                             ) -> ValueAssertion[SymbolReference]:
    return matches_reference_2(symbol_name,
                               is_any_data_type_reference_restrictions())


def is_reference_to_string_made_up_of_just_strings(symbol_name: str) -> ValueAssertion[SymbolReference]:
    return matches_reference_2(
        symbol_name,
        concrete_restriction_assertion.is_string_made_up_of_just_strings_reference_restrictions()
    )
