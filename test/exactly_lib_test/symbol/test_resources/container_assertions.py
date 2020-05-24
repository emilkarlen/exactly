from typing import Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolDependentValue
from exactly_lib.type_system.value_type import ValueType, TypeCategory, LogicValueType, LOGIC_TYPE_2_VALUE_TYPE, \
    DataValueType, DATA_TYPE_2_VALUE_TYPE
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.section_document.test_resources import source_location_assertions as asrt_source_loc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.test_resources import line_source_assertions as asrt_line_source


def matches_container(value_type: ValueAssertion[ValueType],
                      type_category: ValueAssertion[TypeCategory],
                      sdv: ValueAssertion[SymbolDependentValue],
                      data_value_type__if_is_data_type: Optional[ValueAssertion[DataValueType]] = None,
                      logic_value_type__if_is_logic_type: Optional[ValueAssertion[LogicValueType]] = None,
                      definition_source: ValueAssertion[LineSequence] = asrt_line_source.is_line_sequence(),
                      source_location: ValueAssertion[Optional[SourceLocationInfo]] = asrt.anything_goes(),
                      ) -> ValueAssertion[SymbolContainer]:
    components = [
        asrt.sub_component('value_type',
                           SymbolContainer.value_type.fget,
                           value_type),
        asrt.sub_component('type_category',
                           SymbolContainer.type_category.fget,
                           type_category),
    ]
    if data_value_type__if_is_data_type is not None:
        components.append(
            asrt.sub_component('data_value_type__if_is_data_type',
                               SymbolContainer.data_value_type__if_is_data_type.fget,
                               data_value_type__if_is_data_type)

        )
    if logic_value_type__if_is_logic_type is not None:
        components.append(
            asrt.sub_component('logic_value_type__if_is_logic_type',
                               SymbolContainer.logic_value_type__if_is_logic_type.fget,
                               logic_value_type__if_is_logic_type)

        )
    components += [
        asrt.sub_component('definition_source',
                           SymbolContainer.definition_source.fget,
                           definition_source),
        asrt.sub_component('source_location',
                           SymbolContainer.source_location.fget,
                           asrt.is_optional_instance_with(SourceLocationInfo, source_location)),
        asrt.sub_component('sdv',
                           SymbolContainer.sdv.fget,
                           sdv)
    ]
    return asrt.is_instance_with(
        SymbolContainer,
        asrt.and_(components))


def matches_container_of_logic_type(
        logic_value_type: LogicValueType,
        sdv: ValueAssertion[SymbolDependentValue],
        definition_source: ValueAssertion[LineSequence] = asrt_line_source.is_line_sequence(),
) -> ValueAssertion[SymbolContainer]:
    return matches_container(
        value_type=asrt.is_(LOGIC_TYPE_2_VALUE_TYPE[logic_value_type]),
        type_category=asrt.is_(TypeCategory.LOGIC),
        logic_value_type__if_is_logic_type=asrt.is_(logic_value_type),
        sdv=sdv,
        definition_source=definition_source,
        source_location=asrt.is_none_or_instance_with(SourceLocationInfo,
                                                      asrt_source_loc.is_valid_source_location_info())
    )


def matches_container_of_data_type(
        data_value_type: DataValueType,
        sdv: ValueAssertion[SymbolDependentValue],
        definition_source: ValueAssertion[LineSequence] = asrt_line_source.is_line_sequence(),
) -> ValueAssertion[SymbolContainer]:
    return matches_container(
        value_type=asrt.is_(DATA_TYPE_2_VALUE_TYPE[data_value_type]),
        type_category=asrt.is_(TypeCategory.DATA),
        data_value_type__if_is_data_type=asrt.is_(data_value_type),
        sdv=sdv,
        definition_source=definition_source,
        source_location=asrt.is_none_or_instance_with(SourceLocationInfo,
                                                      asrt_source_loc.is_valid_source_location_info())
    )
