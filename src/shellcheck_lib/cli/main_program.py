import os

from shellcheck_lib.cli.program_modes import main_program_argument_parsing as case_argument_parsing
from shellcheck_lib.cli.program_modes.help import argument_parsing as parse_help
from shellcheck_lib.cli.program_modes.help.request_rendering import print_help
from shellcheck_lib.cli.program_modes.test_case.settings import TestCaseExecutionSettings
from shellcheck_lib.cli.program_modes.test_suite import argument_parsing as suite_argument_parsing
from shellcheck_lib.cli.program_modes.test_suite.settings import Settings
from shellcheck_lib.help.contents_structure import application_help_for
from shellcheck_lib.test_case.instruction_setup import InstructionsSetup
from shellcheck_lib.util import argument_parsing_utils
from shellcheck_lib.util.std import StdOutputFiles

EXIT_INVALID_USAGE = 2

HELP_COMMAND = 'help'
SUITE_COMMAND = 'suite'

COMMAND_DESCRIPTIONS = {
    HELP_COMMAND: 'Help system (use "help help" for help on help.)',
    SUITE_COMMAND: 'Executes a test suite: suite SUITE-FILE'
}


class MainProgram:
    def __init__(self,
                 output: StdOutputFiles,
                 instruction_set: InstructionsSetup):
        self._output = output
        self._instruction_set = instruction_set

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

    @property
    def _std(self) -> StdOutputFiles:
        return self._output

    def _parse_and_execute_test_case(self, command_line_arguments: list) -> int:
        settings = case_argument_parsing.parse(command_line_arguments,
                                               COMMAND_DESCRIPTIONS)
        return self.execute_test_case(settings)

    def _parse_and_execute_test_suite(self, command_line_arguments: list) -> int:
        settings = suite_argument_parsing.parse(command_line_arguments)
        return self.execute_test_suite(settings)

    def _parse_and_execute_help(self, help_command_arguments: list) -> int:
        try:
            application_help = application_help_for(self._instruction_set)
            settings = parse_help.parse(application_help,
                                        help_command_arguments)
        except parse_help.HelpError as ex:
            self._output.err.write(ex.msg + os.linesep)
            return EXIT_INVALID_USAGE
        print_help(self._output.out, application_help, settings)
        return 0

    def _parse_and_exit_on_error(self, parse_arguments_and_execute_callable, arguments: list) -> int:
        try:
            return parse_arguments_and_execute_callable(arguments)
        except argument_parsing_utils.ArgumentParsingError as ex:
            self._std.err.write(ex.error_message)
            self._std.err.write(os.linesep)
            return EXIT_INVALID_USAGE
