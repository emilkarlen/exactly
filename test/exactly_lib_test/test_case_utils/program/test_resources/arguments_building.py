from exactly_lib.definitions import instruction_arguments
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments, ArgumentElements
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_resources.arguments_building import ArgumentElementRenderer, Stringable
from exactly_lib_test.test_resources.programs import python_program_execution


def shell_command(command_line: Stringable) -> ArgumentElements:
    return ArgumentElements([shell_command_line(command_line)])


def shell_command_line(command_line: Stringable) -> ArgumentElementRenderer:
    return ab.sequence([syntax_elements.SHELL_COMMAND_TOKEN, command_line])


def symbol_ref_command_line(command_line: Stringable) -> ArgumentElementRenderer:
    return ab.sequence([syntax_elements.SYMBOL_REF_PROGRAM_TOKEN, command_line])


def system_program_command_line(command_line: Stringable) -> ArgumentElementRenderer:
    return ab.sequence([syntax_elements.SYSTEM_PROGRAM_TOKEN, command_line])


def interpret_py_source(python_source: Stringable) -> Arguments:
    return interpret_py_source_elements(python_source).as_arguments


def interpret_py_source_elements(python_source: Stringable) -> ArgumentElements:
    return ArgumentElements([interpret_py_source_line(python_source)])


def system_program_argument_elements(command_line: Stringable) -> ArgumentElements:
    return ArgumentElements([syntax_elements.SYSTEM_PROGRAM_TOKEN, command_line])


def interpret_py_source_line(python_source: Stringable) -> ArgumentElementRenderer:
    return ab.sequence([
        ab.option(syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME),
        python_program_execution.PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE,
        syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER,
        python_source
    ])


def interpret_py_source_file(py_file: Stringable) -> ArgumentElementRenderer:
    return ab.sequence([
        ab.option(syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME),
        ab.option(syntax_elements.EXISTING_FILE_OPTION_NAME),
        py_file
    ])


def program(program_arg: Stringable,
            transformation=None) -> ArgumentElements:
    extra = []
    if transformation:
        extra.append([ab.option(instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME,
                                transformation)])

    return ArgumentElements([program_arg], extra)


def arbitrary_value_on_single_line() -> str:
    return shell_command('ls').as_arguments.lines[0]
