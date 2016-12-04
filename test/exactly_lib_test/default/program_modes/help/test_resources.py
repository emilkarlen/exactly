from exactly_lib.cli.cli_environment.common_cli_options import HELP_COMMAND
from exactly_lib_test.test_resources.main_program.constant_arguments_check import Arrangement
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions.value_assertion_str import is_not_only_space


class HelpInvokation(Arrangement):
    def __init__(self,
                 help_arguments: list):
        self.help_arguments = help_arguments

    def command_line_arguments(self) -> list:
        return [HELP_COMMAND] + self.help_arguments


RESULT_IS_SUCCESSFUL = va.And([pr.is_result_for_exit_code(0),
                               pr.stdout(is_not_only_space())])
