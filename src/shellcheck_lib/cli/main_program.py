import os
import sys

from shellcheck_lib.cli.execution_mode.test_case.settings import TestCaseExecutionSettings
from shellcheck_lib.cli.execution_mode.help.settings import HelpSettings
from shellcheck_lib.cli.execution_mode.test_case import argument_parsing
from shellcheck_lib.cli import argument_parsing_utils
from shellcheck_lib.cli.execution_mode.help.argument_parsing import parse as parse_help


EXIT_INVALID_USAGE = 2

HELP_COMMAND = 'help'


class StdOutputFiles:
    def __init__(self,
                 stdout_file=sys.stdout,
                 stderr_file=sys.stderr):
        self._stdout_file = stdout_file
        self._stderr_file = stderr_file

    @property
    def out(self):
        return self._stdout_file

    @property
    def err(self):
        return self._stderr_file


class MainProgram:
    def __init__(self,
                 output: StdOutputFiles):
        self._output = output

    def execute(self, command_line_arguments: list) -> int:
        if len(command_line_arguments) > 0 and command_line_arguments[0] == HELP_COMMAND:
            return self._parse_and_exit_on_error(self._parse_and_execute_help,
                                                 command_line_arguments[1:])
        return self._parse_and_exit_on_error(self._parse_and_execute_test_case,
                                             command_line_arguments)

    def execute_test_case(self,
                          settings: TestCaseExecutionSettings) -> int:
        raise NotImplementedError()

    def execute_help(self,
                     settings: HelpSettings) -> int:
        raise NotImplementedError()

    @property
    def _std(self) -> StdOutputFiles:
        return self._output

    def _parse_and_execute_test_case(self, command_line_arguments: list) -> int:
        test_case_execution_settings = argument_parsing.parse(command_line_arguments)
        return self.execute_test_case(test_case_execution_settings)

    def _parse_and_execute_help(self, help_command_arguments: list) -> int:
        settings = parse_help(help_command_arguments)
        return self.execute_help(settings)

    def _parse_and_exit_on_error(self, parse_arguments_and_execute_callable, arguments: list) -> int:
        try:
            return parse_arguments_and_execute_callable(arguments)
        except argument_parsing_utils.ArgumentParsingError as ex:
            self._std.err.write(ex.error_message)
            self._std.err.write(os.linesep)
            return EXIT_INVALID_USAGE
