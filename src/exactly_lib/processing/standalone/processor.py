import pathlib
from typing import Optional

from exactly_lib.definitions.test_suite import file_names
from exactly_lib.processing import test_case_processing, processors
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.standalone import result_reporting
from exactly_lib.processing.standalone.settings import TestCaseExecutionSettings, ReportingOption
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
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
            handling_setup = self._resolve_handling_setup(settings.handling_setup,
                                                          settings.test_case_file_path,
                                                          settings.run_as_part_of_explicit_suite)
        except SuiteSyntaxError as ex:
            reporter = result_reporting.TestSuiteSyntaxErrorReporter(std_output_files)
            return reporter.report(ex)
        configuration = processors.Configuration(self._test_case_definition,
                                                 handling_setup,
                                                 self._act_phase_os_process_executor,
                                                 result_reporter.depends_on_result_in_sandbox(),
                                                 settings.sandbox_root_dir_resolver,
                                                 result_reporter.execute_atc_and_skip_assertions())
        result = self._process(settings.test_case_file_path,
                               configuration)
        return result_reporter.report(result)

    @staticmethod
    def _process(test_case_file_path: pathlib.Path,
                 configuration: processors.Configuration,
                 ) -> test_case_processing.Result:
        processor = processors.new_processor_that_is_allowed_to_pollute_current_process(configuration)
        return processor.apply(test_case_processing.test_case_reference_of_source_file(test_case_file_path))

    @staticmethod
    def _get_reporter(std_output_files: StdOutputFiles,
                      reporting_option: ReportingOption) -> result_reporting.TestCaseResultReporter:
        return result_reporting.RESULT_REPORTERS[reporting_option](std_output_files)

    def _resolve_handling_setup(self,
                                default_handling_setup: TestCaseHandlingSetup,
                                test_case_file_path: pathlib.Path,
                                explicit_suite_file_path: Optional[pathlib.Path]) -> TestCaseHandlingSetup:
        def get_suite_file() -> Optional[pathlib.Path]:
            if explicit_suite_file_path:
                return explicit_suite_file_path

            default_suite_file_path = test_case_file_path.parent / file_names.DEFAULT_SUITE_FILE
            if default_suite_file_path.is_file():
                return default_suite_file_path

            return None

        suite_file_path = get_suite_file()

        if not suite_file_path:
            return default_handling_setup
        from exactly_lib.test_suite.file_reading.suite_file_reading import resolve_handling_setup_from_suite_file
        return resolve_handling_setup_from_suite_file(default_handling_setup,
                                                      self._suite_configuration_section_parser,
                                                      self._test_case_definition.parsing_setup,
                                                      suite_file_path)
