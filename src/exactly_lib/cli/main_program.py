import os

import exactly_lib.cli.program_modes.help.error
from exactly_lib.cli.cli_environment.common_cli_options import HELP_COMMAND, SUITE_COMMAND
from exactly_lib.cli.program_modes.test_case import argument_parsing as case_argument_parsing
from exactly_lib.cli.program_modes.test_case.settings import TestCaseExecutionSettings
from exactly_lib.cli.program_modes.test_suite.settings import TestSuiteExecutionSettings
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.util import argument_parsing_utils
from exactly_lib.util.std import StdOutputFiles

EXIT_INVALID_USAGE = 2

COMMAND_DESCRIPTIONS = {
    HELP_COMMAND: 'Help system (use "help help" for help on help.)',
    SUITE_COMMAND: 'Executes a test suite: suite SUITE-FILE'
}


class MainProgram:
    def __init__(self,
                 output: StdOutputFiles,
                 instruction_set: InstructionsSetup,
                 configuration_section_instructions: dict,
                 default: TestCaseHandlingSetup):
        """
        :param configuration_section_instructions: instruction-name -> `SingleInstructionSetup`
        """

        self._output = output
        self._instruction_set = instruction_set
        self._configuration_section_instructions = configuration_section_instructions
        self._default = default

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
                           test_suite_execution_settings: TestSuiteExecutionSettings) -> int:
        raise NotImplementedError()

    @property
    def _std(self) -> StdOutputFiles:
        return self._output

    def _parse_and_execute_test_case(self, command_line_arguments: list) -> int:
        settings = case_argument_parsing.parse(self._default,
                                               command_line_arguments,
                                               COMMAND_DESCRIPTIONS)
        return self.execute_test_case(settings)

    def _parse_and_execute_test_suite(self, command_line_arguments: list) -> int:
        from exactly_lib.cli.program_modes.test_suite import argument_parsing
        settings = argument_parsing.parse(self._default,
                                          command_line_arguments)
        return self.execute_test_suite(settings)

    def _parse_and_execute_help(self, help_command_arguments: list) -> int:
        from exactly_lib.cli.program_modes.help import argument_parsing
        from exactly_lib.cli.program_modes.help.request_handling.resolving_and_handling import handle_help_request
        from exactly_lib.help.the_application_help import new_application_help
        try:
            application_help = new_application_help(self._instruction_set,
                                                    self._configuration_section_instructions)
            help_request = argument_parsing.parse(application_help,
                                                  help_command_arguments)
        except exactly_lib.cli.program_modes.help.error.HelpError as ex:
            self._output.err.write(ex.msg + os.linesep)
            return EXIT_INVALID_USAGE
        handle_help_request(self._output, application_help, help_request)
        return 0

    def _parse_and_exit_on_error(self, parse_arguments_and_execute_callable, arguments: list) -> int:
        try:
            return parse_arguments_and_execute_callable(arguments)
        except argument_parsing_utils.ArgumentParsingError as ex:
            self._std.err.write(ex.error_message)
            self._std.err.write(os.linesep)
            return EXIT_INVALID_USAGE
