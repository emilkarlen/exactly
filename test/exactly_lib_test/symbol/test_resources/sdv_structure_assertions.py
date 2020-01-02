from exactly_lib.symbol import sdv_structure as rs, sdv_structure
from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeSdv, get_logic_value_type
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.value_type import LogicValueType, TypeCategory
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.test_resources.types import LOGIC_VALUE_TYPE_2_VALUE_TYPE
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


def is_sdv_of_logic_type(logic_value_type: LogicValueType) -> ValueAssertion[rs.SymbolDependentValue]:
    value_type = LOGIC_VALUE_TYPE_2_VALUE_TYPE[logic_value_type]
    return asrt.is_instance_with(LogicTypeSdv,
                                 asrt.and_([
                                     asrt.sub_component('type_category',
                                                        rs.get_type_category,
                                                        asrt.is_(TypeCategory.LOGIC)),

                                     asrt.sub_component('logic_value_type',
                                                        get_logic_value_type,
                                                        asrt.is_(logic_value_type)),

                                     asrt.sub_component('value_type',
                                                        rs.get_value_type,
                                                        asrt.is_(value_type)),

                                     asrt.sub_component('references',
                                                        sdv_structure.get_references,
                                                        asrt.is_sequence_of(asrt.is_instance(SymbolReference))),
                                 ]))
