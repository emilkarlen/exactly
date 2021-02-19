from exactly_lib.common.process_result_reporter import ProcessResultReporter, Environment
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
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_suite.file_reading.exception import SuiteParseError


class Processor:
    def __init__(self,
                 test_case_definition: TestCaseDefinition,
                 os_services: OsServices,
                 suite_configuration_section_parser: SectionElementParser,
                 mem_buff_size: int,
                 ):
        self._test_case_definition = test_case_definition
        self._os_services = os_services
        self._suite_configuration_section_parser = suite_configuration_section_parser
        self._mem_buff_size = mem_buff_size

    def process(self,
                reporting_environment: Environment,
                settings: TestCaseExecutionSettings,
                ) -> int:
        result_reporter = self._get_reporter(reporting_environment, settings.reporting_option)

        try:
            processor = self._processor(settings, result_reporter)
        except SuiteParseError as ex:
            reporter = result_reporting.TestSuiteParseErrorReporter(reporting_environment)
            return reporter.report(ex)

        test_case_path = test_case_processing.test_case_reference_of_source_file(settings.test_case_file_path)

        result = processor.apply(test_case_path)

        return result_reporter.report(result)

    @staticmethod
    def _get_reporter(reporting_environment: Environment,
                      reporting_option: ReportingOption) -> result_reporting.TestCaseResultReporter:
        return result_reporting.RESULT_REPORTERS[reporting_option](reporting_environment)

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
            self._test_case_definition.predefined_properties.default_environ_getter,
            self._test_case_definition.predefined_properties.environ,
            self._test_case_definition.predefined_properties.timeout_in_seconds,
            self._os_services,
            sandbox_root_dir_resolver,
            self._mem_buff_size,
            self._test_case_definition.predefined_properties.predefined_symbols,
            result_reporter.execute_atc_and_skip_assertions()
        )
        return processors.new_executor_that_may_pollute_current_processes2(exe_conf,
                                                                           act_phase_setup,
                                                                           is_keep_sandbox)


class ProcessorExecutionReporter(ProcessResultReporter):
    def __init__(self,
                 processor: Processor,
                 settings: TestCaseExecutionSettings,
                 ):
        self._processor = processor
        self._settings = settings

    def report(self, environment: Environment) -> int:
        return self._processor.process(environment, self._settings)
