from exactly_lib.help_texts import instruction_arguments
from exactly_lib.test_case_utils.external_program import syntax_elements
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments, ArgumentElements
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_resources.arguments_building import ArgumentElementRenderer, SequenceOfArguments, Stringable
from exactly_lib_test.test_resources.programs import python_program_execution


def shell_command(command_line: Stringable) -> Arguments:
    return shell_command_elements(command_line).as_arguments


def shell_command_elements(command_line: Stringable) -> ArgumentElements:
    return ArgumentElements([shell_command_line(command_line)])


def shell_command_line(command_line: Stringable) -> ArgumentElementRenderer:
    return SequenceOfArguments([syntax_elements.SHELL_COMMAND_TOKEN, command_line])


def interpret_py_source(python_source: Stringable) -> Arguments:
    return interpret_py_source_elements(python_source).as_arguments


def interpret_py_source_elements(python_source: Stringable) -> ArgumentElements:
    return ArgumentElements([interpret_py_source_line(python_source)])


def interpret_py_source_line(python_source: Stringable) -> ArgumentElementRenderer:
    return SequenceOfArguments([
        syntax_elements.LIST_DELIMITER_START,
        ab.option(syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME),
        python_program_execution.PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE,
        syntax_elements.LIST_DELIMITER_END,
        ab.option(syntax_elements.SOURCE_OPTION_NAME),
        python_source
    ])


def interpret_py_source_file(py_file: Stringable) -> ArgumentElementRenderer:
    return SequenceOfArguments([
        ab.option(syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME),
        ab.option(syntax_elements.INTERPRET_OPTION_NAME),
        py_file
    ])


def program(program_arg: Stringable,
            transformation=None) -> Arguments:
    return program_elements(program_arg, transformation).as_arguments


def program_elements(program_arg: Stringable,
                     transformation=None) -> ArgumentElements:
    extra = []
    if transformation:
        extra.append([ab.option(instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME,
                                transformation)])

    return ArgumentElements([program_arg], extra)
