import os

from shellcheck_lib.cli.execution_mode.test_case.settings import TestCaseExecutionSettings
from shellcheck_lib.cli.execution_mode.help.settings import HelpSettings
from shellcheck_lib.cli.execution_mode.test_case import argument_parsing as case_argument_parsing
from shellcheck_lib.cli.execution_mode.test_suite import argument_parsing as suite_argument_parsing
from shellcheck_lib.cli import argument_parsing_utils
from shellcheck_lib.cli.execution_mode.help.argument_parsing import parse as parse_help
from shellcheck_lib.cli.execution_mode.test_suite.settings import Settings
from shellcheck_lib.general.output import StdOutputFiles


EXIT_INVALID_USAGE = 2

HELP_COMMAND = 'help'
SUITE_COMMAND = 'suite'


class MainProgram:
    def __init__(self,
                 output: StdOutputFiles):
        self._output = output

    def execute(self, command_line_arguments: list) -> int:
        if len(command_line_arguments) > 0:
            if command_line_arguments[0] == HELP_COMMAND:
                return self._parse_and_exit_on_error(self._parse_and_execute_help,
                                                     command_line_arguments[1:])
            if command_line_arguments[0] == SUITE_COMMAND:
                return self._parse_and_exit_on_error(self._parse_and_execute_test_suite,
                                                     command_line_arguments[1:])
        return self._parse_and_exit_on_error(self._parse_and_execute_test_case,
                                             command_line_arguments)

    def execute_test_case(self,
                          settings: TestCaseExecutionSettings) -> int:
        raise NotImplementedError()

    def execute_test_suite(self,
                           settings: Settings) -> int:
        raise NotImplementedError()

    def execute_help(self,
                     settings: HelpSettings) -> int:
        raise NotImplementedError()

    @property
    def _std(self) -> StdOutputFiles:
        return self._output

    def _parse_and_execute_test_case(self, command_line_arguments: list) -> int:
        settings = case_argument_parsing.parse(command_line_arguments)
        return self.execute_test_case(settings)

    def _parse_and_execute_test_suite(self, command_line_arguments: list) -> int:
        settings = suite_argument_parsing.parse(command_line_arguments)
        return self.execute_test_suite(settings)

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
