from exactly_lib.test_case_utils.external_program import syntax_elements
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments


def shell_command(command_line: str) -> Arguments:
    return Arguments(
        syntax_elements.SHELL_COMMAND_TOKEN + ' ' + command_line)
