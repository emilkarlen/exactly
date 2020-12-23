import datetime
import pathlib
from typing import Callable, List

from exactly_lib.common.process_result_reporter import ProcessResultReporter, Environment
from exactly_lib.processing import processors as case_processing
from exactly_lib.processing import test_case_processing
from exactly_lib.section_document.source_location import source_location_path_of
from exactly_lib.test_case import error_description
from exactly_lib.test_suite import reporting
from exactly_lib.test_suite import structure
from exactly_lib.test_suite.enumeration import SuiteEnumerator
from exactly_lib.test_suite.file_reading.exception import SuiteReadError
from exactly_lib.test_suite.file_reading.suite_hierarchy_reading import SuiteHierarchyReader
from exactly_lib.test_suite.reporting import RootSuiteReporter, TestCaseProcessingInfo
from exactly_lib.test_suite.result_reporters import SuiteReadErrorReporter

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

    def process(self, suite_root_file_path: pathlib.Path, reporting_environment: Environment) -> int:
        reporter = self.process_reporter(suite_root_file_path)
        return reporter.report(reporting_environment)

    def process_reporter(self, suite_root_file_path: pathlib.Path) -> ProcessResultReporter:
        try:
            root_suite = self._suite_hierarchy_reader.apply(suite_root_file_path)
        except SuiteReadError as ex:
            return SuiteReadErrorReporter(ex, self._reporter)

        return _SuiteExecutionReporter(
            self._default_case_configuration,
            self._reporter,
            self._suite_enumerator,
            self._test_case_processor_constructor,
            root_suite,
            suite_root_file_path,
        )


class _SuiteExecutionReporter(ProcessResultReporter):
    def __init__(self,
                 default_case_configuration: case_processing.Configuration,
                 suite_processing_reporter: reporting.RootSuiteProcessingReporter,
                 suite_enumerator: SuiteEnumerator,
                 test_case_processor_constructor: TestCaseProcessorConstructor,
                 root_suite: structure.TestSuiteHierarchy,
                 suite_root_file_path: pathlib.Path,
                 ):
        self._root_suite = root_suite
        self._suite_root_file_path = suite_root_file_path
        self._suite_processing_reporter = suite_processing_reporter
        self._suite_enumerator = suite_enumerator
        self._default_case_configuration = default_case_configuration
        self._test_case_processor_constructor = test_case_processor_constructor

    def report(self, environment: Environment) -> int:
        suits_in_processing_order = self._suite_enumerator.apply(self._root_suite)
        executor = SuitesExecutor(self._suite_processing_reporter.execution_reporter(self._root_suite,
                                                                                     environment,
                                                                                     self._suite_root_file_path),
                                  self._default_case_configuration,
                                  self._test_case_processor_constructor)
        return executor.execute_and_report(suits_in_processing_order)


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
        Executes a single suite (i.e. not its sub suites).
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
            self._default_case_configuration.os_services,
            self._default_case_configuration.mem_buff_size,
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
