from exactly_lib.test_case_utils.external_program import syntax_elements
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_resources.programs import python_program_execution


def shell_command(command_line: str) -> Arguments:
    return Arguments(syntax_elements.SHELL_COMMAND_TOKEN + ' ' + command_line)


def interpret_py_source(python_source: str) -> Arguments:
    return Arguments(
        ' '.join([syntax_elements.LIST_DELIMITER_START,
                  syntax_elements.PYTHON_EXECUTABLE_OPTION_STRING,
                  python_program_execution.PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE,
                  syntax_elements.LIST_DELIMITER_END,
                  syntax_elements.SOURCE_OPTION,
                  python_source])
    )
