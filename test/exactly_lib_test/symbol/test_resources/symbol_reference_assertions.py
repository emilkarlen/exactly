from exactly_lib.symbol import symbol_usage as su
from exactly_lib.symbol.restriction import ReferenceRestrictions
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
