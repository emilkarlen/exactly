from shellcheck_lib.cli.execution_mode.test_case.settings import TestCaseExecutionSettings
from shellcheck_lib.cli.execution_mode.help.settings import HelpSettings


EXIT_INVALID_USAGE = 2


class MainProgram:
    def execute(self,
                command_line_arguments: list) -> int:
        raise NotImplementedError()

    def execute_test_case(self,
                          settings: TestCaseExecutionSettings) -> int:
        raise NotImplementedError()

    def execute_help(self,
                     settings: HelpSettings) -> int:
        raise NotImplementedError()
