from exactly_lib.symbol import resolver_structure as rs, symbol_usage as su
from exactly_lib.symbol.restriction import ReferenceRestrictions
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources import line_source_assertions as asrt_line_source


def matches_container(assertion_on_resolver: asrt.ValueAssertion[rs.SymbolValueResolver],
                      assertion_on_source: asrt.ValueAssertion[LineSequence] = asrt_line_source.is_line_sequence(),
                      ) -> asrt.ValueAssertion[rs.SymbolContainer]:
    return asrt.is_instance_with(
        rs.SymbolContainer,
        asrt.and_([
            asrt.sub_component('source',
                               rs.SymbolContainer.definition_source.fget,
                               assertion_on_source),
            asrt.sub_component('resolver',
                               rs.SymbolContainer.resolver.fget,
                               assertion_on_resolver)
        ]))


def matches_definition(assertion_on_name: asrt.ValueAssertion[str],
                       assertion_on_container: asrt.ValueAssertion[rs.SymbolContainer],
                       ) -> asrt.ValueAssertion[su.SymbolDefinition]:
    return asrt.is_instance_with(
        su.SymbolDefinition,
        asrt.And([
            asrt.sub_component('name',
                               su.SymbolDefinition.name.fget,
                               asrt.is_instance_with(str,
                                                     assertion_on_name)),
            asrt.sub_component('resolver_container',
                               su.SymbolDefinition.resolver_container.fget,
                               asrt.is_instance_with(rs.SymbolContainer,
                                                     assertion_on_container)),

        ])
    )


def matches_reference(assertion_on_name: asrt.ValueAssertion[str] = asrt.anything_goes(),
                      assertion_on_restrictions: asrt.ValueAssertion[ReferenceRestrictions] = asrt.anything_goes()
                      ) -> asrt.ValueAssertion[su.SymbolUsage]:
    return asrt.is_instance_with(
        su.SymbolReference,
        asrt.and_([
            asrt.sub_component('name',
                               su.SymbolReference.name.fget,
                               assertion_on_name),
            asrt.sub_component('restrictions',
                               su.SymbolReference.restrictions.fget,
                               assertion_on_restrictions)

        ]))


def matches_reference_2(expected_name: str,
                        assertion_on_restrictions: asrt.ValueAssertion[ReferenceRestrictions] = asrt.anything_goes()
                        ) -> asrt.ValueAssertion[su.SymbolUsage]:
    return matches_reference(asrt.equals(expected_name),
                             assertion_on_restrictions)
