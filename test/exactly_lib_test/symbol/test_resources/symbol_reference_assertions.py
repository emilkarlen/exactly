from exactly_lib.symbol.sdv_structure import ReferenceRestrictions, SymbolReference
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def matches_reference(assertion_on_name: Assertion[str] = asrt.anything_goes(),
                      assertion_on_restrictions: Assertion[ReferenceRestrictions] = asrt.anything_goes()
                      ) -> Assertion[SymbolReference]:
    return asrt.and_([
        asrt.sub_component('name',
                           SymbolReference.name.fget,
                           assertion_on_name),
        asrt.sub_component('restrictions',
                           SymbolReference.restrictions.fget,
                           assertion_on_restrictions)

    ])


def matches_reference_2(expected_name: str,
                        assertion_on_restrictions: Assertion[ReferenceRestrictions] = asrt.anything_goes()
                        ) -> Assertion[SymbolReference]:
    return matches_reference(asrt.equals(expected_name),
                             assertion_on_restrictions)
