from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import types
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.test_resources import arguments_building
from exactly_lib_test.test_resources.arguments_building import ArgumentElementsRenderer
from exactly_lib_test.test_resources.strings import WithToString

VALUE_TYPE_INFOS = {
    type_info.value_type: type_info
    for type_info in types.ALL_TYPES_INFO_TUPLE
}


def symbol_def_instruction(type_: ValueType, name: str, value: WithToString) -> ArgumentElementsRenderer:
    return arguments_building.SequenceOfElements(
        [instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME] +
        symbol_def_arguments(type_, name, value).elements
    )


def symbol_def_arguments(type_: ValueType, name: str, value: WithToString) -> ArgumentElementsRenderer:
    return arguments_building.SequenceOfElements(
        (
            VALUE_TYPE_INFOS[type_].identifier,
            name,
            instruction_arguments.ASSIGNMENT_OPERATOR,
            value,
        )
    )
