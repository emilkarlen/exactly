from exactly_lib.symbol import symbol_usage as su
from exactly_lib.symbol.data.restrictions.reference_restrictions import ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.data.restrictions.value_restrictions import StringRestriction
from exactly_lib.symbol.restriction import ReferenceRestrictions
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    is_any_data_type_reference_restrictions
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_reference
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def matches_reference(assertion_on_name: asrt.ValueAssertion[str] = asrt.anything_goes(),
                      assertion_on_restrictions: asrt.ValueAssertion[ReferenceRestrictions] = asrt.anything_goes()
                      ) -> asrt.ValueAssertion[su.SymbolReference]:
    return asrt.and_([
        asrt.sub_component('name',
                           su.SymbolReference.name.fget,
                           assertion_on_name),
        asrt.sub_component('restrictions',
                           su.SymbolReference.restrictions.fget,
                           assertion_on_restrictions)

    ])


def matches_reference_2(expected_name: str,
                        assertion_on_restrictions: asrt.ValueAssertion[ReferenceRestrictions] = asrt.anything_goes()
                        ) -> asrt.ValueAssertion[su.SymbolReference]:
    return matches_reference(asrt.equals(expected_name),
                             assertion_on_restrictions)


def is_reference_data_type_symbol(symbol_name: str) -> asrt.ValueAssertion[su.SymbolReference]:
    return matches_reference_2(symbol_name,
                               is_any_data_type_reference_restrictions())


def is_reference_to_string_made_up_of_just_plain_strings(symbol_name: str) -> asrt.ValueAssertion[SymbolReference]:
    return equals_symbol_reference(
        SymbolReference(symbol_name,
                        string_made_up_of_just_strings_reference_restrictions()))


def string_made_up_of_just_strings_reference_restrictions() -> ReferenceRestrictionsOnDirectAndIndirect:
    return ReferenceRestrictionsOnDirectAndIndirect(StringRestriction(),
                                                    StringRestriction())
