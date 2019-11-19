from exactly_lib.symbol import sdv_structure as rs
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.test_resources import line_source_assertions as asrt_line_source


def matches_container(assertion_on_sdv: ValueAssertion[rs.SymbolDependentValue],
                      assertion_on_source: ValueAssertion[LineSequence] = asrt_line_source.is_line_sequence(),
                      ) -> ValueAssertion[rs.SymbolContainer]:
    return asrt.is_instance_with(
        rs.SymbolContainer,
        asrt.and_([
            asrt.sub_component('source',
                               rs.SymbolContainer.definition_source.fget,
                               assertion_on_source),
            asrt.sub_component('sdv',
                               rs.SymbolContainer.sdv.fget,
                               assertion_on_sdv)
        ]))
