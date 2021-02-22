from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference
from exactly_lib.type_val_deps.sym_ref.data.data_value_restriction import ValueRestriction
from exactly_lib.type_val_deps.sym_ref.restrictions import DataTypeReferenceRestrictions
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import matches_reference_2
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.data import data_restrictions_assertions as asrt_data_ref_restriction
from exactly_lib_test.type_val_deps.test_resources.data.data_restrictions_assertions import \
    is_reference_restrictions__on_direct_and_indirect, equals_reference_restrictions__convertible_to_string


def matches_symbol_reference_with_restriction_on_direct_target(
        expected_name: str,
        assertion_on_direct_restriction: Assertion[ValueRestriction]
) -> Assertion[SymbolReference]:
    return asrt_sym_ref.matches_reference_2(expected_name,
                                            is_reference_restrictions__on_direct_and_indirect(
                                                assertion_on_direct=assertion_on_direct_restriction,
                                                assertion_on_every=asrt.ValueIsNone()))


def equals_data_type_symbol_reference(expected: SymbolReference) -> Assertion[SymbolReference]:
    restrictions = expected.restrictions
    if not isinstance(restrictions, DataTypeReferenceRestrictions):
        raise ValueError('Restrictions must be {}. Found {}'.format(
            DataTypeReferenceRestrictions,
            restrictions,
        ))
    return asrt_sym_ref.matches_reference_2(expected.name,
                                            equals_reference_restrictions__convertible_to_string(restrictions))


def matches_data_type_symbol_reference(symbol_name: str,
                                       restrictions: DataTypeReferenceRestrictions) -> Assertion[SymbolReference]:
    return asrt_sym_ref.matches_reference_2(symbol_name,
                                            equals_reference_restrictions__convertible_to_string(restrictions))


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
    def reference_assertion(self) -> Assertion[SymbolReference]:
        return matches_data_type_symbol_reference(self.name, self.restrictions)


def symbol_usage_equals_data_type_symbol_reference(expected: SymbolReference) -> Assertion[SymbolUsage]:
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
            equals_reference_restrictions__convertible_to_string(restrictions)))


def equals_symbol_references__convertible_to_string(expected: Sequence[SymbolReference]
                                                    ) -> Assertion[Sequence[SymbolReference]]:
    return asrt.matches_sequence([
        equals_data_type_symbol_reference(expected_ref)
        for expected_ref in expected
    ])


def is_reference_to__convertible_to_string(symbol_name: str
                                           ) -> Assertion[SymbolReference]:
    return matches_reference_2(
        symbol_name,
        asrt_data_ref_restriction.is_reference_restrictions__convertible_to_string(),
    )


def is_reference_to_string_made_up_of_just_strings(symbol_name: str) -> Assertion[SymbolReference]:
    return matches_reference_2(
        symbol_name,
        asrt_data_ref_restriction.is_reference_restrictions__string_made_up_of_just_strings()
    )
