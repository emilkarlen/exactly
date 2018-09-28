from exactly_lib.symbol import resolver_structure as rs, symbol_usage as su
from exactly_lib.symbol.restriction import ReferenceRestrictions
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def matches_definition(name: ValueAssertion[str],
                       container: ValueAssertion[rs.SymbolContainer],
                       ) -> ValueAssertion[su.SymbolDefinition]:
    return asrt.is_instance_with(
        su.SymbolDefinition,
        asrt.And([
            asrt.sub_component('name',
                               su.SymbolDefinition.name.fget,
                               asrt.is_instance_with(str,
                                                     name)),
            asrt.sub_component('resolver_container',
                               su.SymbolDefinition.resolver_container.fget,
                               asrt.is_instance_with(rs.SymbolContainer,
                                                     container)),

        ])
    )


def matches_reference(assertion_on_name: ValueAssertion[str] = asrt.anything_goes(),
                      assertion_on_restrictions: ValueAssertion[ReferenceRestrictions] = asrt.anything_goes()
                      ) -> ValueAssertion[su.SymbolUsage]:
    return asrt.is_sub_class_with(
        su.SymbolReference,
        asrt_sym_ref.matches_reference(assertion_on_name, assertion_on_restrictions))


def matches_reference_2(expected_name: str,
                        assertion_on_restrictions: ValueAssertion[ReferenceRestrictions] = asrt.anything_goes()
                        ) -> ValueAssertion[su.SymbolUsage]:
    return matches_reference(asrt.equals(expected_name),
                             assertion_on_restrictions)
