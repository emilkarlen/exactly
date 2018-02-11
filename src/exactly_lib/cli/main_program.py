import os
import types
from typing import List, Dict

from exactly_lib.cli.cli_environment import exit_codes
from exactly_lib.cli.cli_environment.common_cli_options import HELP_COMMAND, SUITE_COMMAND
from exactly_lib.cli.program_modes.test_case import argument_parsing as case_argument_parsing
from exactly_lib.cli.program_modes.test_case import execution as test_case_execution
from exactly_lib.cli.program_modes.test_case.settings import TestCaseExecutionSettings
from exactly_lib.cli.program_modes.test_suite.settings import TestSuiteExecutionSettings
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.execution.full_execution import PredefinedProperties
from exactly_lib.help.entities.builtin.contents_structure import BuiltinSymbolDocumentation
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.section_document import document_parser
from exactly_lib.symbol.resolver_structure import SymbolValueResolver, container_of_builtin
from exactly_lib.util import argument_parsing_utils
from exactly_lib.util.std import StdOutputFiles
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.util.textformat.structure.document import SectionContents

COMMAND_DESCRIPTIONS = {
    HELP_COMMAND: 'Help system (use "help help" for help on help.)',
    SUITE_COMMAND: 'Executes a test suite: suite SUITE-FILE'
}


class BuiltinSymbol:
    def __init__(self,
                 name: str,
                 resolver: SymbolValueResolver,
                 single_line_description: str,
                 documentation: SectionContents,
                 ):
        self._name = name
        self._resolver = resolver
        self._single_line_description = single_line_description
        self._documentation = documentation

    @property
    def name(self) -> str:
        return self._name

    @property
    def as_name_and_container_pair(self):
        return self._name, container_of_builtin(self._resolver)

    @property
    def resolver(self) -> SymbolValueResolver:
        return self._resolver

    @property
    def documentation(self) -> BuiltinSymbolDocumentation:
        return BuiltinSymbolDocumentation(self._resolver.value_type, self.name,
                                          self._single_line_description,
                                          self._documentation)


class TestCaseDefinitionForMainProgram:
    """
    Corresponds to TestCaseDefinition, but with
    extra information about predefined symbols for the help system.
    """

    def __init__(self,
                 test_case_parsing_setup: TestCaseParsingSetup,
                 builtin_symbols: List[BuiltinSymbol]):
        self.test_case_parsing_setup = test_case_parsing_setup
        self.builtin_symbols = builtin_symbols


class TestSuiteDefinition(tuple):
    def __new__(cls,
                configuration_section_instructions: Dict[str, SingleInstructionSetup],
                configuration_section_parser: document_parser.SectionElementParser,
                get_sds_root_name_prefix: types.FunctionType = lambda: ''):
        return tuple.__new__(cls, (configuration_section_instructions,
                                   configuration_section_parser,
                                   get_sds_root_name_prefix))

    @property
    def configuration_section_instructions(self) -> Dict[str, SingleInstructionSetup]:
        """
        :rtype instruction-name -> `SingleInstructionSetup`
        """
        return self[0]

    @property
    def configuration_section_parser(self) -> document_parser.SectionElementParser:
        return self[1]

    @property
    def get_sds_root_name_prefix(self) -> types.FunctionType:
        return self[2]


class MainProgram:
    def __init__(self,
                 output: StdOutputFiles,
                 default_test_case_handling_setup: TestCaseHandlingSetup,
                 test_case_definition: TestCaseDefinitionForMainProgram,
                 test_suite_definition: TestSuiteDefinition,
                 ):

        self._test_suite_definition = test_suite_definition
        self._test_case_definition = TestCaseDefinition(
            test_case_definition.test_case_parsing_setup,
            PredefinedProperties(
                SymbolTable(dict(map(BuiltinSymbol.as_name_and_container_pair.fget,
                                     test_case_definition.builtin_symbols)))
            )
        )
        self._output = output
        self._default_test_case_handling_setup = default_test_case_handling_setup
        self._test_case_def_for_m_p = test_case_definition

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
        return test_case_execution.execute(self._std,
                                           self._test_case_definition,
                                           self._test_suite_definition.configuration_section_parser,
                                           settings)

    def execute_test_suite(self,
                           test_suite_execution_settings: TestSuiteExecutionSettings) -> int:
        from exactly_lib.processing import processors
        from exactly_lib.test_suite import enumeration
        from exactly_lib.test_suite import suite_hierarchy_reading
        from exactly_lib.test_suite import execution
        default_configuration = processors.Configuration(self._test_case_definition,
                                                         test_suite_execution_settings.handling_setup,
                                                         False,
                                                         self._test_suite_definition.get_sds_root_name_prefix())
        executor = execution.Executor(default_configuration,
                                      self._output,
                                      suite_hierarchy_reading.Reader(
                                          suite_hierarchy_reading.Environment(
                                              self._test_suite_definition.configuration_section_parser,
                                              self._test_case_definition.parsing_setup,
                                              default_configuration.default_handling_setup)
                                      ),
                                      test_suite_execution_settings.reporter_factory,
                                      enumeration.DepthFirstEnumerator(),
                                      processors.new_processor_that_should_not_pollute_current_process,
                                      test_suite_execution_settings.suite_root_file_path)
        return executor.execute()

    @property
    def _std(self) -> StdOutputFiles:
        return self._output

    def _parse_and_execute_test_case(self, command_line_arguments: list) -> int:
        settings = case_argument_parsing.parse(self._default_test_case_handling_setup,
                                               command_line_arguments,
                                               COMMAND_DESCRIPTIONS)
        return self.execute_test_case(settings)

    def _parse_and_execute_test_suite(self, command_line_arguments: list) -> int:
        from exactly_lib.cli.program_modes.test_suite import argument_parsing
        settings = argument_parsing.parse(self._default_test_case_handling_setup,
                                          command_line_arguments)
        return self.execute_test_suite(settings)

    def _parse_and_execute_help(self, help_command_arguments: list) -> int:
        from exactly_lib.cli.program_modes.help import argument_parsing
        from exactly_lib.cli.program_modes.help.request_handling.resolving_and_handling import handle_help_request
        from exactly_lib.help.the_application_help import new_application_help
        from exactly_lib.cli.program_modes.help.error import HelpError

        builtin_symbol_documentation_list = [
            builtin_symbol.documentation
            for builtin_symbol in self._test_case_def_for_m_p.builtin_symbols
        ]
        application_help = new_application_help(
            self._test_case_def_for_m_p.test_case_parsing_setup.instruction_setup,
            self._test_suite_definition.configuration_section_instructions,
            builtin_symbol_documentation_list,
        )
        try:
            help_request = argument_parsing.parse(application_help,
                                                  help_command_arguments)
        except HelpError as ex:
            self._output.err.write(ex.msg + os.linesep)
            return exit_codes.EXIT_INVALID_USAGE
        handle_help_request(self._output, application_help, help_request)
        return 0

    def _parse_and_exit_on_error(self, parse_arguments_and_execute_callable, arguments: list) -> int:
        try:
            return parse_arguments_and_execute_callable(arguments)
        except argument_parsing_utils.ArgumentParsingError as ex:
            self._std.err.write(ex.error_message)
            self._std.err.write(os.linesep)
            return exit_codes.EXIT_INVALID_USAGE
