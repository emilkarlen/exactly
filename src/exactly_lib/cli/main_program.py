import os
from typing import List, Callable

from exactly_lib.cli.program_modes.test_suite.settings import TestSuiteExecutionSettings
from exactly_lib.cli.test_case_def import TestCaseDefinitionForMainProgram
from exactly_lib.cli.test_suite_def import TestSuiteDefinition
from exactly_lib.common.process_result_reporter import Environment, ProcessResultReporter
from exactly_lib.common.process_result_reporters import ProcessResultReporterWithInitialExitValueOutput
from exactly_lib.execution.configuration import PredefinedProperties
from exactly_lib.execution.sandbox_dir_resolving import SandboxRootDirNameResolver
from exactly_lib.impls.os_services import os_services_access
from exactly_lib.processing import exit_values
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.standalone.settings import TestCaseExecutionSettings
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.util import argument_parsing_utils
from exactly_lib.util.file_utils.std import StdOutputFiles
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.symbol_table import SymbolTable
from .definitions import common_cli_options, exit_codes
from ..definitions import os_proc_env


class MainProgram:
    def __init__(self,
                 default_test_case_handling_setup: TestCaseHandlingSetup,
                 default_case_sandbox_root_dir_name_sdv: SandboxRootDirNameResolver,
                 test_case_definition: TestCaseDefinitionForMainProgram,
                 test_suite_definition: TestSuiteDefinition,
                 mem_buff_size: int,
                 ):

        self._test_suite_definition = test_suite_definition
        predefined_symbols = SymbolTable(
            {
                bs.name: bs.container
                for bs in test_case_definition.builtin_symbols
            }
        )
        self._mem_buff_size = mem_buff_size
        self._test_case_definition = TestCaseDefinition(
            test_case_definition.test_case_parsing_setup,
            PredefinedProperties(
                os_proc_env.ENV_VARS_GETTER__DEFAULT,
                os_proc_env.ENV_VARS__DEFAULT,
                os_proc_env.TIMEOUT__DEFAULT,
                predefined_symbols,
            )
        )
        self._default_test_case_handling_setup = default_test_case_handling_setup
        self._test_case_def_for_m_p = test_case_definition
        self._default_case_sandbox_root_dir_name_sdv = default_case_sandbox_root_dir_name_sdv

        self._commands = {
            common_cli_options.HELP_COMMAND: self._parse_and_execute_help,
            common_cli_options.SUITE_COMMAND: self._parse_and_execute_test_suite,
            common_cli_options.SYMBOL_COMMAND: self._parse_and_execute_symbol_inspection
        }

    def execute(self,
                command_line_arguments: List[str],
                output: StdOutputFiles) -> int:
        reporter = self._get_reporter(command_line_arguments)
        return reporter.report(Environment.new_with_color_if_supported_by_terminal(output))

    def _get_reporter(self,
                      command_line_arguments: List[str]) -> ProcessResultReporter:
        try:
            if len(command_line_arguments) > 0:
                if command_line_arguments[0] in self._commands:
                    return _parse_and_exit_on_error(self._commands[command_line_arguments[0]],
                                                    command_line_arguments[1:])
            return _parse_and_exit_on_error(self._parse_and_execute_test_case,
                                            command_line_arguments)
        except _StartupError as ex:
            return ex.result

    def execute_test_case(self,
                          settings: TestCaseExecutionSettings,
                          ) -> ProcessResultReporter:
        from exactly_lib.processing.standalone import processor

        the_processor = processor.Processor(self._test_case_definition,
                                            _resolve_os_services(),
                                            self._test_suite_definition.configuration_section_parser,
                                            self._mem_buff_size)
        return processor.ProcessorExecutionReporter(the_processor, settings)

    def execute_test_suite(self,
                           settings: TestSuiteExecutionSettings,
                           ) -> ProcessResultReporter:
        from exactly_lib.processing import processors
        from exactly_lib.test_suite import enumeration
        from exactly_lib.test_suite.file_reading import suite_hierarchy_reading
        from exactly_lib.test_suite import processing

        default_configuration = processors.Configuration(self._test_case_definition,
                                                         settings.handling_setup,
                                                         _resolve_os_services(),
                                                         self._mem_buff_size,
                                                         False,
                                                         self._test_suite_definition.sandbox_root_dir_sdv)
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
        return processor.process_reporter(settings.suite_root_file_path)

    def _parse_and_execute_test_case(self,
                                     command_line_arguments: List[str],
                                     ) -> ProcessResultReporter:
        from exactly_lib.cli.program_modes.test_case import argument_parsing

        settings = argument_parsing.parse(self._default_test_case_handling_setup,
                                          self._default_case_sandbox_root_dir_name_sdv,
                                          command_line_arguments,
                                          common_cli_options.COMMAND_DESCRIPTIONS)
        return self.execute_test_case(settings)

    def _parse_and_execute_test_suite(self,
                                      command_line_arguments: List[str],
                                      ) -> ProcessResultReporter:
        from exactly_lib.cli.program_modes.test_suite import argument_parsing
        settings = argument_parsing.parse(self._default_test_case_handling_setup,
                                          command_line_arguments)
        return self.execute_test_suite(settings)

    def _parse_and_execute_symbol_inspection(self,
                                             command_line_arguments: List[str],
                                             ) -> ProcessResultReporter:
        from exactly_lib.cli.program_modes.symbol import argument_parsing, execution

        request = argument_parsing.parse(self._default_test_case_handling_setup,
                                         self._default_case_sandbox_root_dir_name_sdv,
                                         command_line_arguments,
                                         common_cli_options.COMMAND_DESCRIPTIONS)
        executor = execution.Executor(
            self._test_case_definition,
            self._test_suite_definition.configuration_section_parser,
        )

        return executor.execution_reporter(request)

    def _parse_and_execute_help(self,
                                help_command_arguments: List[str],
                                ) -> ProcessResultReporter:
        from exactly_lib.cli.program_modes.help import argument_parsing
        from exactly_lib.cli.program_modes.help.request_handling.resolving_and_handling import handle_help_request_rr
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
            return _InvalidUsageReporter(ex.msg)

        return handle_help_request_rr(application_help, help_request)


class _StartupError(Exception):
    def __init__(self, result: ProcessResultReporter):
        self.result = result


def _parse_and_exit_on_error(parse_arguments_and_execute_callable: Callable[[List[str]], ProcessResultReporter],
                             arguments: List[str],
                             ) -> ProcessResultReporter:
    try:
        return parse_arguments_and_execute_callable(arguments)
    except argument_parsing_utils.ArgumentParsingError as ex:
        raise _StartupError(_InvalidUsageReporter(ex.error_message))


def _resolve_os_services() -> OsServices:
    try:
        return os_services_access.new_for_current_os()
    except os_services_access.OsServicesError as ex:
        def print_ex_msg(environment: Environment):
            printer = environment.std_file_printers.get(ProcOutputFile.STDERR)
            printer.write_line(ex.msg)

        raise _StartupError(
            ProcessResultReporterWithInitialExitValueOutput(
                exit_values.EXECUTION__INTERNAL_ERROR,
                ProcOutputFile.STDOUT,
                print_ex_msg)
        )


class _InvalidUsageReporter(ProcessResultReporter):
    def __init__(self, error_message: str):
        self._error_message = error_message

    def report(self, environment: Environment) -> int:
        output_file = environment.std_files.err

        output_file.write(self._error_message)
        output_file.write(os.linesep)
        return exit_codes.EXIT_INVALID_USAGE
