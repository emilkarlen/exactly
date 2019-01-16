import os
from typing import List, Dict, Callable, Sequence

from exactly_lib.cli.definitions import common_cli_options
from exactly_lib.cli.definitions import exit_codes
from exactly_lib.cli.program_modes.test_suite.settings import TestSuiteExecutionSettings
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.execution import sandbox_dir_resolving
from exactly_lib.execution.configuration import PredefinedProperties
from exactly_lib.execution.sandbox_dir_resolving import SandboxRootDirNameResolver
from exactly_lib.help.entities.builtin.contents_structure import BuiltinSymbolDocumentation
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.standalone.settings import TestCaseExecutionSettings
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.symbol.resolver_structure import SymbolValueResolver, container_of_builtin, SymbolContainer
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor
from exactly_lib.util import argument_parsing_utils
from exactly_lib.util.std import StdOutputFiles
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.util.textformat.structure.document import SectionContents


class BuiltinSymbol:
    def __init__(self,
                 name: str,
                 resolver: SymbolValueResolver,
                 single_line_description: str,
                 documentation: SectionContents,
                 see_also: Sequence[SeeAlsoTarget] = (),
                 ):
        self._name = name
        self._resolver = resolver
        self._single_line_description = single_line_description
        self._documentation = documentation
        self._see_also = see_also

    @property
    def name(self) -> str:
        return self._name

    @property
    def container(self) -> SymbolContainer:
        return container_of_builtin(self._resolver)

    @property
    def documentation(self) -> BuiltinSymbolDocumentation:
        return BuiltinSymbolDocumentation(self._resolver.value_type,
                                          self.name,
                                          self._single_line_description,
                                          self._documentation,
                                          self._see_also)


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
                configuration_section_parser: SectionElementParser,
                get_sds_root_name_prefix: Callable[[], str] = lambda: ''):
        return tuple.__new__(cls, (configuration_section_instructions,
                                   configuration_section_parser,
                                   get_sds_root_name_prefix))

    @property
    def configuration_section_instructions(self) -> Dict[str, SingleInstructionSetup]:
        return self[0]

    @property
    def configuration_section_parser(self) -> SectionElementParser:
        return self[1]

    @property
    def sandbox_root_dir_resolver(self) -> SandboxRootDirNameResolver:
        return sandbox_dir_resolving.mk_tmp_dir_with_prefix(self.__get_sds_root_name_prefix())

    @property
    def __get_sds_root_name_prefix(self) -> Callable[[], str]:
        return self[2]


class MainProgram:
    def __init__(self,
                 default_test_case_handling_setup: TestCaseHandlingSetup,
                 default_case_sandbox_root_dir_name_resolver: SandboxRootDirNameResolver,
                 act_phase_os_process_executor: ActPhaseOsProcessExecutor,
                 test_case_definition: TestCaseDefinitionForMainProgram,
                 test_suite_definition: TestSuiteDefinition,
                 ):

        self._test_suite_definition = test_suite_definition
        predefined_symbols = SymbolTable(
            {
                bs.name: bs.container
                for bs in test_case_definition.builtin_symbols
            }
        )
        self._test_case_definition = TestCaseDefinition(
            test_case_definition.test_case_parsing_setup,
            PredefinedProperties(
                os.environ,
                predefined_symbols,
            )
        )
        self._act_phase_os_process_executor = act_phase_os_process_executor
        self._default_test_case_handling_setup = default_test_case_handling_setup
        self._test_case_def_for_m_p = test_case_definition
        self._default_case_sandbox_root_dir_name_resolver = default_case_sandbox_root_dir_name_resolver

        self._commands = {
            common_cli_options.HELP_COMMAND: self._parse_and_execute_help,
            common_cli_options.SUITE_COMMAND: self._parse_and_execute_test_suite,
            common_cli_options.SYMBOL_COMMAND: self._parse_and_execute_symbol_inspection
        }

    def execute(self,
                command_line_arguments: List[str],
                output: StdOutputFiles) -> int:
        if len(command_line_arguments) > 0:
            if command_line_arguments[0] in self._commands:
                return _parse_and_exit_on_error(self._commands[command_line_arguments[0]],
                                                command_line_arguments[1:],
                                                output)
        return _parse_and_exit_on_error(self._parse_and_execute_test_case,
                                        command_line_arguments,
                                        output)

    def execute_test_case(self,
                          settings: TestCaseExecutionSettings,
                          output: StdOutputFiles,
                          ) -> int:
        from exactly_lib.processing.standalone import processor
        processor = processor.Processor(self._test_case_definition,
                                        self._act_phase_os_process_executor,
                                        self._test_suite_definition.configuration_section_parser)
        return processor.process(output, settings)

    def execute_test_suite(self,
                           settings: TestSuiteExecutionSettings,
                           output: StdOutputFiles,
                           ) -> int:
        from exactly_lib.processing import processors
        from exactly_lib.test_suite import enumeration
        from exactly_lib.test_suite.file_reading import suite_hierarchy_reading
        from exactly_lib.test_suite import processing
        default_configuration = processors.Configuration(self._test_case_definition,
                                                         settings.handling_setup,
                                                         self._act_phase_os_process_executor,
                                                         False,
                                                         self._test_suite_definition.sandbox_root_dir_resolver)
        processor = processing.Processor(default_configuration,
                                         suite_hierarchy_reading.Reader(
                                             suite_hierarchy_reading.Environment(
                                                 self._test_suite_definition.configuration_section_parser,
                                                 self._test_case_definition.parsing_setup,
                                                 default_configuration.default_handling_setup)
                                         ),
                                         settings.processing_reporter,
                                         enumeration.DepthFirstEnumerator(),
                                         processors.new_processor_that_should_not_pollute_current_process)
        return processor.process(settings.suite_root_file_path, output)

    def _parse_and_execute_test_case(self,
                                     command_line_arguments: List[str],
                                     output: StdOutputFiles,
                                     ) -> int:
        from exactly_lib.cli.program_modes.test_case import argument_parsing

        settings = argument_parsing.parse(self._default_test_case_handling_setup,
                                          self._default_case_sandbox_root_dir_name_resolver,
                                          command_line_arguments,
                                          common_cli_options.COMMAND_DESCRIPTIONS)
        return self.execute_test_case(settings, output)

    def _parse_and_execute_test_suite(self,
                                      command_line_arguments: List[str],
                                      output: StdOutputFiles,
                                      ) -> int:
        from exactly_lib.cli.program_modes.test_suite import argument_parsing
        settings = argument_parsing.parse(self._default_test_case_handling_setup,
                                          command_line_arguments)
        return self.execute_test_suite(settings, output)

    def _parse_and_execute_symbol_inspection(self,
                                             command_line_arguments: List[str],
                                             output: StdOutputFiles,
                                             ) -> int:
        from exactly_lib.cli.program_modes.symbol import argument_parsing, execution

        request = argument_parsing.parse(self._default_test_case_handling_setup,
                                         self._default_case_sandbox_root_dir_name_resolver,
                                         command_line_arguments,
                                         common_cli_options.COMMAND_DESCRIPTIONS)
        executor = execution.Executor(request,
                                      self._test_case_definition,
                                      self._test_suite_definition.configuration_section_parser,
                                      output)
        return executor.execute()

    def _parse_and_execute_help(self,
                                help_command_arguments: List[str],
                                output: StdOutputFiles,
                                ) -> int:
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
            return _exit_invalid_usage(output, ex.msg)
        handle_help_request(output, application_help, help_request)
        return 0


def _parse_and_exit_on_error(parse_arguments_and_execute_callable: Callable[[List[str], StdOutputFiles], int],
                             arguments: List[str],
                             output: StdOutputFiles,
                             ) -> int:
    try:
        return parse_arguments_and_execute_callable(arguments, output)
    except argument_parsing_utils.ArgumentParsingError as ex:
        return _exit_invalid_usage(output, ex.error_message)


def _exit_invalid_usage(output: StdOutputFiles,
                        error_message: str) -> int:
    output.err.write(error_message)
    output.err.write(os.linesep)
    return exit_codes.EXIT_INVALID_USAGE
