from typing import Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolDependentValue
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.util.test_resources import line_source_assertions as asrt_line_source


def matches_container(value_type: Assertion[ValueType],
                      sdv: Assertion[SymbolDependentValue],
                      definition_source: Assertion[LineSequence] = asrt_line_source.is_line_sequence(),
                      source_location: Assertion[Optional[SourceLocationInfo]] = asrt.anything_goes(),
                      ) -> Assertion[SymbolContainer]:
    components = [
        asrt.sub_component('value_type',
                           SymbolContainer.value_type.fget,
                           value_type),
    ]
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
