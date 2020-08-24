from typing import Sequence, Optional

from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.definitions.primitives.string_transformer import WITH_TRANSFORMED_CONTENTS_OPTION_NAME
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments, ArgumentElements
from exactly_lib_test.test_case_utils.string_transformers.test_resources.argument_syntax import \
    syntax_for_transformer_option
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_resources import argument_renderer as primitive_ab
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.programs import python_program_execution
from exactly_lib_test.test_resources.strings import WithToString


def symbol_ref_command_line(command_line: WithToString) -> ArgumentElementsRenderer:
    return ab.sequence([syntax_elements.SYMBOL_REF_PROGRAM_TOKEN, command_line])


def symbol_ref_command_elements(symbol_name: str,
                                arguments: Sequence = (),
                                transformation: Optional[str] = None) -> ArgumentElements:
    first_line = [syntax_elements.SYMBOL_REF_PROGRAM_TOKEN, symbol_name] + list(arguments)

    following_lines = []

    if transformation is not None:
        following_lines.append([syntax_for_transformer_option(transformation)])

    return ArgumentElements(first_line, following_lines)


def shell_command(command_line: WithToString) -> ArgumentElements:
    return ArgumentElements([shell_command_line(command_line)])


def shell_command_line(command_line: WithToString) -> ArgumentElementsRenderer:
    return ab.sequence([syntax_elements.SHELL_COMMAND_TOKEN, command_line])


def system_program_argument_elements(command_line: WithToString) -> ArgumentElements:
    return ArgumentElements([syntax_elements.SYSTEM_PROGRAM_TOKEN, command_line])


def executable_file_command_line(executable_file: WithToString) -> ArgumentElementsRenderer:
    return ab.singleton(executable_file)


def system_program_command_line(command_line: WithToString) -> ArgumentElementsRenderer:
    return ab.sequence([syntax_elements.SYSTEM_PROGRAM_TOKEN, command_line])


def interpret_py_source(python_source: WithToString) -> Arguments:
    return interpret_py_source_elements(python_source).as_arguments


def py_interpreter_command_line() -> ArgumentElementsRenderer:
    return ab.option(syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME)


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


def interpret_py_source_file_elements(py_file: WithToString) -> ArgumentElements:
    return ArgumentElements([interpret_py_source_file(py_file)])


def program(program_arg: WithToString,
            transformation: Optional[WithToString] = None,
            ) -> ArgumentElements:
    extra = []
    if transformation:
        extra.append([ab.option(
            string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME,
            transformation)])

    return ArgumentElements([program_arg], extra)


def arbitrary_value_on_single_line() -> str:
    return shell_command('ls').as_arguments.lines[0]


def program_followed_by_transformation(
        program_wo_transformation: ArgumentElementsRenderer,
        transformation: ArgumentElementsRenderer
) -> ArgumentElementsRenderer:
    return primitive_ab.SeparatedByNewLine(
        program_wo_transformation,
        primitive_ab.SequenceOfArguments([
            ab.option(WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
            transformation,
        ])
    )


def program_w_superfluous_args() -> ArgumentElementsRenderer:
    return program_followed_by_transformation(
        system_program_command_line('system-program'),
        ab.sequence__r([
            ab.symbol_reference('TRANSFORMER_SYMBOL'),
            ab.singleton('superfluous')
        ])
    )
