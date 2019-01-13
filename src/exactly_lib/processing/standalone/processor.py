from exactly_lib.execution.configuration import ExecutionConfiguration
from exactly_lib.execution.sandbox_dir_resolving import SandboxRootDirNameResolver
from exactly_lib.processing import test_case_processing, processors, processing_utils
from exactly_lib.processing import test_case_processing as processing
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.standalone import result_reporting
from exactly_lib.processing.standalone.accessor_resolver import AccessorResolver
from exactly_lib.processing.standalone.settings import TestCaseExecutionSettings, ReportingOption
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor
from exactly_lib.test_suite.file_reading.exception import SuiteSyntaxError
from exactly_lib.util.std import StdOutputFiles


class Processor:
    def __init__(self,
                 test_case_definition: TestCaseDefinition,
                 act_phase_os_process_executor: ActPhaseOsProcessExecutor,
                 suite_configuration_section_parser: SectionElementParser):
        self._test_case_definition = test_case_definition
        self._act_phase_os_process_executor = act_phase_os_process_executor
        self._suite_configuration_section_parser = suite_configuration_section_parser

    def process(self,
                std_output_files: StdOutputFiles,
                settings: TestCaseExecutionSettings,
                ) -> int:
        result_reporter = self._get_reporter(std_output_files, settings.reporting_option)

        try:
            processor = self._processor(settings, result_reporter)
        except SuiteSyntaxError as ex:
            reporter = result_reporting.TestSuiteSyntaxErrorReporter(std_output_files)
            return reporter.report(ex)

        test_case_file_ref = test_case_processing.test_case_reference_of_source_file(settings.test_case_file_path)

        result = processor.apply(test_case_file_ref)

        return result_reporter.report(result)

    @staticmethod
    def _get_reporter(std_output_files: StdOutputFiles,
                      reporting_option: ReportingOption) -> result_reporting.TestCaseResultReporter:
        return result_reporting.RESULT_REPORTERS[reporting_option](std_output_files)

    def _processor(self,
                   settings: TestCaseExecutionSettings,
                   result_reporter: result_reporting.TestCaseResultReporter
                   ) -> processing.Processor:
        accessor_resolver = AccessorResolver(self._test_case_definition.parsing_setup,
                                             self._suite_configuration_section_parser,
                                             settings.handling_setup,
                                             )
        accessor, act_phase_setup = accessor_resolver.resolve(settings.test_case_file_path,
                                                              settings.run_as_part_of_explicit_suite)

        executor = self._executor(act_phase_setup,
                                  result_reporter.depends_on_result_in_sandbox(),
                                  settings.sandbox_root_dir_resolver,
                                  result_reporter)

        return processing_utils.ProcessorFromAccessorAndExecutor(
            accessor,
            executor
        )

    def _executor(self,
                  act_phase_setup: ActPhaseSetup,
                  is_keep_sandbox: bool,
                  sandbox_root_dir_resolver: SandboxRootDirNameResolver,
                  result_reporter: result_reporting.TestCaseResultReporter
                  ) -> processing_utils.Executor:
        exe_conf = ExecutionConfiguration(
            self._test_case_definition.predefined_properties.environ,
            self._act_phase_os_process_executor,
            sandbox_root_dir_resolver,
            self._test_case_definition.predefined_properties.predefined_symbols,
            result_reporter.execute_atc_and_skip_assertions()
        )
        return processors.new_executor_that_may_pollute_current_processes2(exe_conf,
                                                                           act_phase_setup,
                                                                           is_keep_sandbox)
