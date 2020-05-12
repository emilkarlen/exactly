from typing import Type, Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol import sdv_structure
from exactly_lib.symbol.logic.logic_type_sdv import LogicSdv
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolContainer, SymbolDependentValue
from exactly_lib.type_system.value_type import ValueType, TypeCategory, LogicValueType, LOGIC_TYPE_2_VALUE_TYPE
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.section_document.test_resources import source_location_assertions as asrt_source_loc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.test_resources import line_source_assertions as asrt_line_source


def matches_container(value_type: ValueAssertion[ValueType],
                      type_category: ValueAssertion[TypeCategory],
                      assertion_on_sdv: ValueAssertion[SymbolDependentValue],
                      assertion_on_source: ValueAssertion[LineSequence] = asrt_line_source.is_line_sequence(),
                      source_location: ValueAssertion[Optional[SourceLocationInfo]] = asrt.anything_goes(),
                      ) -> ValueAssertion[SymbolContainer]:
    return asrt.is_instance_with(
        SymbolContainer,
        asrt.and_([
            asrt.sub_component('value_type',
                               SymbolContainer.value_type.fget,
                               value_type),
            asrt.sub_component('type_category',
                               SymbolContainer.type_category.fget,
                               type_category),
            asrt.sub_component('definition_source',
                               SymbolContainer.definition_source.fget,
                               assertion_on_source),
            asrt.sub_component('source_location',
                               SymbolContainer.source_location.fget,
                               asrt.is_optional_instance_with(SourceLocationInfo, source_location)),
            asrt.sub_component('sdv',
                               SymbolContainer.sdv.fget,
                               assertion_on_sdv)
        ]))


def matches_container__sdv(value_type: ValueAssertion[ValueType],
                           type_category: ValueAssertion[TypeCategory],
                           assertion_on_sdv: ValueAssertion[SymbolDependentValue],
                           assertion_on_source: ValueAssertion[LineSequence] = asrt_line_source.is_line_sequence(),
                           source_location: ValueAssertion[Optional[SourceLocationInfo]] = asrt.anything_goes(),
                           ) -> ValueAssertion[SymbolContainer]:
    return asrt.is_instance_with(
        SymbolContainer,
        asrt.and_([
            asrt.sub_component('value_type',
                               SymbolContainer.value_type.fget,
                               value_type),
            asrt.sub_component('type_category',
                               SymbolContainer.type_category.fget,
                               type_category),
            asrt.sub_component('definition_source',
                               SymbolContainer.definition_source.fget,
                               assertion_on_source),
            asrt.sub_component('source_location',
                               SymbolContainer.source_location.fget,
                               asrt.is_optional_instance_with(SourceLocationInfo, source_location)),
            asrt.sub_component('sdv',
                               SymbolContainer.sdv.fget,
                               assertion_on_sdv)
        ]))


def matches_container_of_logic_type(
        logic_value_type: LogicValueType,
        assertion_on_sdv: ValueAssertion[SymbolDependentValue],
        assertion_on_source: ValueAssertion[LineSequence] = asrt_line_source.is_line_sequence(),
) -> ValueAssertion[SymbolContainer]:
    return matches_container__sdv(
        value_type=asrt.is_(LOGIC_TYPE_2_VALUE_TYPE[logic_value_type]),
        type_category=asrt.is_(TypeCategory.LOGIC),
        assertion_on_sdv=assertion_on_sdv,
        assertion_on_source=assertion_on_source,
        source_location=asrt.is_none_or_instance_with(SourceLocationInfo,
                                                      asrt_source_loc.is_valid_source_location_info())
    )


def is_sdv_of_logic_type(class_: Type[LogicSdv]) -> ValueAssertion[SymbolDependentValue]:
    return asrt.is_instance_with(
        class_,
        asrt.sub_component('references',
                           sdv_structure.get_references,
                           asrt.is_sequence_of(asrt.is_instance(SymbolReference))),
    )
