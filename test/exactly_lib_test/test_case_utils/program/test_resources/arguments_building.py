from typing import Sequence

from exactly_lib.definitions import instruction_arguments
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments, ArgumentElements
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_resources.arguments_building import ArgumentElementsRenderer
from exactly_lib_test.test_resources.programs import python_program_execution
from exactly_lib_test.test_resources.strings import WithToString


def symbol_ref_command_line(command_line: WithToString) -> ArgumentElementsRenderer:
    return ab.sequence([syntax_elements.SYMBOL_REF_PROGRAM_TOKEN, command_line])


def symbol_ref_command_elements(symbol_name: str, arguments: Sequence = ()) -> ArgumentElements:
    return ArgumentElements([syntax_elements.SYMBOL_REF_PROGRAM_TOKEN, symbol_name] +
                            list(arguments))


def shell_command(command_line: WithToString) -> ArgumentElements:
    return ArgumentElements([shell_command_line(command_line)])


def shell_command_line(command_line: WithToString) -> ArgumentElementsRenderer:
    return ab.sequence([syntax_elements.SHELL_COMMAND_TOKEN, command_line])


def system_program_argument_elements(command_line: WithToString) -> ArgumentElements:
    return ArgumentElements([syntax_elements.SYSTEM_PROGRAM_TOKEN, command_line])


def system_program_command_line(command_line: WithToString) -> ArgumentElementsRenderer:
    return ab.sequence([syntax_elements.SYSTEM_PROGRAM_TOKEN, command_line])


def interpret_py_source(python_source: WithToString) -> Arguments:
    return interpret_py_source_elements(python_source).as_arguments


def interpret_py_source_elements(python_source: WithToString) -> ArgumentElements:
    return ArgumentElements([interpret_py_source_line(python_source)])


def interpret_py_source_line(python_source: WithToString) -> ArgumentElementsRenderer:
    return ab.sequence([
        ab.option(syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME),
        python_program_execution.PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE,
        syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER,
        python_source
    ])


def interpret_py_source_file(py_file: WithToString) -> ArgumentElementsRenderer:
    return ab.sequence([
        ab.option(syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME),
        ab.option(syntax_elements.EXISTING_FILE_OPTION_NAME),
        py_file
    ])


def program(program_arg: WithToString,
            transformation=None) -> ArgumentElements:
    extra = []
    if transformation:
        extra.append([ab.option(instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME,
                                transformation)])

    return ArgumentElements([program_arg], extra)


def arbitrary_value_on_single_line() -> str:
    return shell_command('ls').as_arguments.lines[0]
