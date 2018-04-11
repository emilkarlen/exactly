from exactly_lib.symbol import resolver_structure as rs
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
