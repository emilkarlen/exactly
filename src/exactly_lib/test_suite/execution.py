import datetime
import pathlib
import types

from exactly_lib.execution.result_reporting import output_location
from exactly_lib.processing import processors as case_processing
from exactly_lib.processing import test_case_processing
from exactly_lib.test_case import error_description
from exactly_lib.test_suite import exit_values
from exactly_lib.test_suite import reporting
from exactly_lib.test_suite import structure
from exactly_lib.test_suite.enumeration import SuiteEnumerator
from exactly_lib.test_suite.instruction_set.parse import SuiteReadError
from exactly_lib.test_suite.reporting import RootSuiteReporter, TestCaseProcessingInfo
from exactly_lib.test_suite.suite_hierarchy_reading import SuiteHierarchyReader
from exactly_lib.util.std import StdOutputFiles, FilePrinter


class Executor:
    """
    Reads a suite file and executes it.
    """

    def __init__(self,
                 default_case_configuration: case_processing.Configuration,
                 output: StdOutputFiles,
                 suite_hierarchy_reader: SuiteHierarchyReader,
                 reporter_factory: reporting.RootSuiteReporterFactory,
                 suite_enumerator: SuiteEnumerator,
                 test_case_processor_constructor,
                 suite_root_file_path: pathlib.Path):
        """
        :param test_case_processor_constructor: `case_processing.Configuration` -> `test_case_processing.Processor`
        """
        self._default_case_configuration = default_case_configuration
        self._std = output
        self._suite_hierarchy_reader = suite_hierarchy_reader
        self._suite_enumerator = suite_enumerator
        self._reporter_factory = reporter_factory
        self._test_case_processor_constructor = test_case_processor_constructor
        self._suite_root_file_path = suite_root_file_path

    def execute(self) -> int:
        return self._execute_and_let_reporter_report_final_result()

    def _execute_and_let_reporter_report_final_result(self) -> int:
        try:
            root_suite = self._read_structure(self._suite_root_file_path)
        except SuiteReadError as ex:
            file_printer = FilePrinter(self._std.err)
            output_location(file_printer,
                            ex.suite_file,
                            ex.maybe_section_name,
                            ex.line,
                            'section')
            file_printer.write_lines(ex.error_message_lines())
            exit_identifier_output_file = FilePrinter(self._std.out)
            exit_value = exit_values.INVALID_SUITE
            self._std.err.flush()
            exit_identifier_output_file.write_line(exit_value.exit_identifier)
            return exit_value.exit_code

        suits_in_processing_order = self._suite_enumerator.apply(root_suite)
        executor = SuitesExecutor(self._reporter_factory.new_reporter(root_suite,
                                                                      self._std,
                                                                      self._suite_root_file_path),
                                  self._default_case_configuration,
                                  self._test_case_processor_constructor)
        return executor.execute_and_report(suits_in_processing_order)

    def _read_structure(self,
                        suite_file_path: pathlib.Path) -> structure.TestSuite:
        return self._suite_hierarchy_reader.apply(suite_file_path)


class SuitesExecutor:
    """
    Executes a list of TestSuite:s.
    """

    def __init__(self,
                 reporter: RootSuiteReporter,
                 default_case_configuration: case_processing.Configuration,
                 test_case_processor_constructor: types.FunctionType):
        self._reporter = reporter
        self._default_case_configuration = default_case_configuration
        self._test_case_processor_constructor = test_case_processor_constructor

    def execute_and_report(self, suits_in_processing_order: list) -> int:
        """
        :param suits_in_processing_order: [TestSuite]
        :return: Exit code for main program.
        """
        self._reporter.root_suite_begin()
        for suite in suits_in_processing_order:
            self._process_single_sub_suite(suite)
        self._reporter.root_suite_end()
        return self._reporter.report_final_results()

    def _process_single_sub_suite(self,
                                  suite: structure.TestSuite):
        """
        Executes a single suite (i.e. not it's sub suites).
        """
        sub_suite_reporter = self._reporter.new_sub_suite_reporter(suite)
        sub_suite_reporter.listener().suite_begin()
        case_processor = self._case_processor_for(suite)
        for case in suite.test_cases:
            sub_suite_reporter.listener().case_begin(case)
            processing_info = _process_and_time(case_processor, case)
            sub_suite_reporter.listener().case_end(case, processing_info.result)
            sub_suite_reporter.case_end(case, processing_info)
        sub_suite_reporter.listener().suite_end()

    def _case_processor_for(self, suite):
        configuration = self._configuration_for_cases_in_suite(suite)
        return self._test_case_processor_constructor(configuration)

    def _configuration_for_cases_in_suite(self, suite: structure.TestSuite) -> case_processing.Configuration:
        return case_processing.Configuration(
            self._default_case_configuration.split_line_into_name_and_argument_function,
            self._default_case_configuration.instruction_setup,
            suite.test_case_handling_setup,
            self._default_case_configuration.is_keep_execution_directory_root,
            self._default_case_configuration.execution_directory_root_name_prefix)


def _process_and_time(case_processor: test_case_processing.Processor,
                      case: test_case_processing.TestCaseSetup) -> TestCaseProcessingInfo:
    case_start_time = datetime.datetime.now()
    result = _process_case(case_processor, case)
    case_end_time = datetime.datetime.now()
    duration = case_end_time - case_start_time
    return TestCaseProcessingInfo(result, duration)


def _process_case(case_processor: test_case_processing.Processor,
                  case: test_case_processing.TestCaseSetup) -> test_case_processing.Result:
    try:
        return case_processor.apply(case)
    except Exception as ex:
        error_info = test_case_processing.ErrorInfo(error_description.of_exception(ex),
                                                    file_path=case.file_path)
        return test_case_processing.new_internal_error(error_info)
