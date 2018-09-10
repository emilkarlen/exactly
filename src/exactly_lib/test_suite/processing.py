import datetime
import pathlib
from typing import Callable, List

from exactly_lib.common.result_reporting import output_location
from exactly_lib.processing import processors as case_processing
from exactly_lib.processing import test_case_processing
from exactly_lib.section_document.source_location import source_location_path_of
from exactly_lib.test_case import error_description
from exactly_lib.test_suite import exit_values
from exactly_lib.test_suite import reporting
from exactly_lib.test_suite import structure
from exactly_lib.test_suite.enumeration import SuiteEnumerator
from exactly_lib.test_suite.file_reading.exception import SuiteReadError
from exactly_lib.test_suite.file_reading.suite_hierarchy_reading import SuiteHierarchyReader
from exactly_lib.test_suite.reporting import RootSuiteReporter, TestCaseProcessingInfo
from exactly_lib.util.std import StdOutputFiles, file_printer_with_color_if_terminal

TestCaseProcessorConstructor = Callable[[case_processing.Configuration], test_case_processing.Processor]


class Processor:
    """
    Reads a suite file and executes it.
    """

    def __init__(self,
                 default_case_configuration: case_processing.Configuration,
                 suite_hierarchy_reader: SuiteHierarchyReader,
                 reporter: reporting.RootSuiteProcessingReporter,
                 suite_enumerator: SuiteEnumerator,
                 test_case_processor_constructor: TestCaseProcessorConstructor):
        self._default_case_configuration = default_case_configuration
        self._suite_hierarchy_reader = suite_hierarchy_reader
        self._suite_enumerator = suite_enumerator
        self._reporter = reporter
        self._test_case_processor_constructor = test_case_processor_constructor

    def process(self, suite_root_file_path: pathlib.Path, output: StdOutputFiles) -> int:
        try:
            root_suite = self._suite_hierarchy_reader.apply(suite_root_file_path)
        except SuiteReadError as ex:
            return self._report_read_error(ex, output)

        suits_in_processing_order = self._suite_enumerator.apply(root_suite)
        executor = SuitesExecutor(self._reporter.execution_reporter(root_suite,
                                                                    output,
                                                                    suite_root_file_path),
                                  self._default_case_configuration,
                                  self._test_case_processor_constructor)
        return executor.execute_and_report(suits_in_processing_order)

    def _report_read_error(self,
                           ex: SuiteReadError,
                           output: StdOutputFiles,
                           ) -> int:
        exit_value = exit_values.INVALID_SUITE
        self._reporter.report_invalid_suite(exit_value, output)
        output.out.flush()
        self._print_error_message(ex, output)
        return exit_value.exit_code

    @staticmethod
    def _print_error_message(ex: SuiteReadError,
                             output: StdOutputFiles,
                             ):
        printer = file_printer_with_color_if_terminal(output.err)
        output_location(printer,
                        ex.source_location,
                        ex.maybe_section_name,
                        None)
        printer.write_lines(ex.error_message_lines())


class SuitesExecutor:
    """
    Executes a list of TestSuite:s.
    """

    def __init__(self,
                 reporter: RootSuiteReporter,
                 default_case_configuration: case_processing.Configuration,
                 test_case_processor_constructor: TestCaseProcessorConstructor):
        self._reporter = reporter
        self._default_case_configuration = default_case_configuration
        self._test_case_processor_constructor = test_case_processor_constructor

    def execute_and_report(self, suits_in_processing_order: List[structure.TestSuiteHierarchy]) -> int:
        """
        :return: Exit code for main program.
        """
        self._reporter.root_suite_begin()
        for suite in suits_in_processing_order:
            self._process_single_sub_suite(suite)
        self._reporter.root_suite_end()
        return self._reporter.report_final_results()

    def _process_single_sub_suite(self, suite: structure.TestSuiteHierarchy):
        """
        Executes a single suite (i.e. not it's sub suites).
        """
        sub_suite_reporter = self._reporter.new_sub_suite_reporter(suite)
        sub_suite_reporter.progress_reporter.suite_begin()
        case_processor = self._case_processor_for(suite)
        for case in suite.test_cases:
            sub_suite_reporter.progress_reporter.case_begin(case)
            processing_info = _process_and_time(case_processor, case)
            sub_suite_reporter.progress_reporter.case_end(case, processing_info)
            sub_suite_reporter.case_end(case, processing_info)
        sub_suite_reporter.progress_reporter.suite_end()

    def _case_processor_for(self, suite: structure.TestSuiteHierarchy) -> test_case_processing.Processor:
        configuration = self._configuration_for_cases_in_suite(suite)
        return self._test_case_processor_constructor(configuration)

    def _configuration_for_cases_in_suite(self, suite: structure.TestSuiteHierarchy) -> case_processing.Configuration:
        return case_processing.Configuration(
            self._default_case_configuration.test_case_definition,
            suite.test_case_handling_setup,
            self._default_case_configuration.act_phase_os_process_executor,
            self._default_case_configuration.is_keep_sandbox,
            self._default_case_configuration.sandbox_root_dir_resolver)


def _process_and_time(case_processor: test_case_processing.Processor,
                      case: test_case_processing.TestCaseFileReference) -> TestCaseProcessingInfo:
    case_start_time = datetime.datetime.now()
    result = _process_case(case_processor, case)
    case_end_time = datetime.datetime.now()
    duration = case_end_time - case_start_time
    return TestCaseProcessingInfo(result, duration)


def _process_case(case_processor: test_case_processing.Processor,
                  case: test_case_processing.TestCaseFileReference) -> test_case_processing.Result:
    try:
        return case_processor.apply(case)
    except Exception as ex:
        error_info = test_case_processing.ErrorInfo(error_description.of_exception(ex),
                                                    source_location_path_of(case.file_path,
                                                                            None)
                                                    )
        return test_case_processing.new_internal_error(error_info)
