from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import types
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.symbol.value_type import ValueType
from exactly_lib_test.test_resources import argument_renderer
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.strings import WithToString

VALUE_TYPE_INFOS = {
    type_info.value_type: type_info
    for type_info in types.ALL_TYPES_INFO_TUPLE
}


def symbol_def_instruction(type_: ValueType, name: str, value: WithToString) -> ArgumentElementsRenderer:
    return argument_renderer.SequenceOfElements(
        [instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME] +
        symbol_def_arguments(type_, name, value).elements
    )


def symbol_def_arguments(type_: ValueType, name: str, value: WithToString) -> ArgumentElementsRenderer:
    return argument_renderer.SequenceOfElements(
        (
            VALUE_TYPE_INFOS[type_].identifier,
            name,
            instruction_arguments.ASSIGNMENT_OPERATOR,
            value,
        )
    )
