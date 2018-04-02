from exactly_lib.help_texts import instruction_arguments
from exactly_lib.test_case_utils.external_program import syntax_elements
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments, ArgumentElements
from exactly_lib_test.test_resources import arguments_building as ab
from exactly_lib_test.test_resources.arguments_building import ArgumentElementRenderer, SequenceOfArguments
from exactly_lib_test.test_resources.programs import python_program_execution


def shell_command(command_line: str) -> Arguments:
    return shell_command_elements(command_line).as_arguments


def shell_command_elements(command_line: str) -> ArgumentElements:
    return ArgumentElements([shell_command_line(command_line)])


def shell_command_line(command_line: str) -> ArgumentElementRenderer:
    return SequenceOfArguments([syntax_elements.SHELL_COMMAND_TOKEN, command_line])


def interpret_py_source(python_source: str) -> Arguments:
    return interpret_py_source_elements(python_source).as_arguments


def interpret_py_source_elements(python_source: str) -> ArgumentElements:
    return ArgumentElements([interpret_py_source_line(python_source)])


def interpret_py_source_line(python_source: str) -> ArgumentElementRenderer:
    return SequenceOfArguments([
        syntax_elements.LIST_DELIMITER_START,
        ab.OptionArgument(syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME),
        python_program_execution.PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE,
        syntax_elements.LIST_DELIMITER_END,
        ab.OptionArgument(syntax_elements.SOURCE_OPTION_NAME),
        python_source
    ])


def program(program_arg: ArgumentElementRenderer,
            transformation=None) -> Arguments:
    return program_elements(program_arg, transformation).as_arguments


def program_elements(program_arg: ArgumentElementRenderer,
                     transformation=None) -> ArgumentElements:
    extra = []
    if transformation:
        extra.append([ab.OptionWithArgument(instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME,
                                            transformation)])

    return ArgumentElements([program_arg], extra)
