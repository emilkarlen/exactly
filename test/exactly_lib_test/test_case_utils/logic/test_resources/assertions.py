from typing import Type, Sequence

from exactly_lib.symbol import sdv_structure
from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib_test.symbol.test_resources.sdv_structure_assertions import is_sdv_of_logic_type
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def matches_logic_sdv_attributes(type_: Type[LogicTypeSdv],
                                 logic_value_type: LogicValueType,
                                 references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                                 ) -> ValueAssertion[LogicTypeSdv]:
    return asrt.is_instance_with(
        type_,
        asrt.and_([
            is_sdv_of_logic_type(logic_value_type),

            asrt.sub_component('references',
                               sdv_structure.get_references,
                               references),
        ])
    )
