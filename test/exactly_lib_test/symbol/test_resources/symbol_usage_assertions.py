from exactly_lib.symbol.sdv_structure import ReferenceRestrictions, SymbolDefinition, SymbolUsage, SymbolReference, \
    SymbolContainer
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def matches_definition(name: Assertion[str],
                       container: Assertion[SymbolContainer],
                       ) -> Assertion[SymbolDefinition]:
    return asrt.is_instance_with(
        SymbolDefinition,
        asrt.And([
            asrt.sub_component('name',
                               SymbolDefinition.name.fget,
                               asrt.is_instance_with(str,
                                                     name)),
            asrt.sub_component('symbol_container',
                               SymbolDefinition.symbol_container.fget,
                               asrt.is_instance_with(SymbolContainer,
                                                     container)),

        ])
    )


def matches_reference(assertion_on_name: Assertion[str] = asrt.anything_goes(),
                      assertion_on_restrictions: Assertion[ReferenceRestrictions] = asrt.anything_goes()
                      ) -> Assertion[SymbolUsage]:
    return asrt.is_sub_class_with(
        SymbolReference,
        asrt_sym_ref.matches_reference(assertion_on_name, assertion_on_restrictions))


def matches_reference__ref(assertion_on_name: Assertion[str] = asrt.anything_goes(),
                           assertion_on_restrictions: Assertion[ReferenceRestrictions] = asrt.anything_goes()
                           ) -> Assertion[SymbolReference]:
    return asrt.is_sub_class_with(
        SymbolReference,
        asrt_sym_ref.matches_reference(assertion_on_name, assertion_on_restrictions))


def matches_reference_2(expected_name: str,
                        assertion_on_restrictions: Assertion[ReferenceRestrictions] = asrt.anything_goes()
                        ) -> Assertion[SymbolUsage]:
    return matches_reference(asrt.equals(expected_name),
                             assertion_on_restrictions)


def matches_reference_2__ref(expected_name: str,
                             assertion_on_restrictions: Assertion[ReferenceRestrictions] = asrt.anything_goes()
                             ) -> Assertion[SymbolReference]:
    return matches_reference__ref(asrt.equals(expected_name),
                                  assertion_on_restrictions)
