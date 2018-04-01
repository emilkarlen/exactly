from exactly_lib.help_texts import instruction_arguments
from exactly_lib.test_case_utils.external_program import syntax_elements
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_resources.arguments_building import ArgumentElementRenderer, SequenceOfArguments, \
    OptionArgument, OptionWithArgument
from exactly_lib_test.test_resources.programs import python_program_execution


def shell_command(command_line: str) -> Arguments:
    return Arguments(shell_command_arg(command_line))


def shell_command_arg(command_line: str) -> ArgumentElementRenderer:
    return SequenceOfArguments([syntax_elements.SHELL_COMMAND_TOKEN, command_line])


def interpret_py_source(python_source: str) -> Arguments:
    return Arguments(interpret_py_source_arg(python_source))


def interpret_py_source_arg(python_source: str) -> ArgumentElementRenderer:
    return SequenceOfArguments(
        [syntax_elements.LIST_DELIMITER_START,
         OptionArgument(syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME),
         python_program_execution.PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE,
         syntax_elements.LIST_DELIMITER_END,
         OptionArgument(syntax_elements.SOURCE_OPTION_NAME),
         python_source]
    )


def program(program_arg: ArgumentElementRenderer,
            transformation=None) -> Arguments:
    extra = []
    if transformation:
        extra.append(OptionWithArgument(instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME,
                                        transformation))

    return Arguments(program_arg, extra)
