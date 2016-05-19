import pathlib

from exactly_lib.cli.cli_environment.exit_value import ExitValue
from exactly_lib.cli.util.error_message_printing import output_location
from exactly_lib.default.program_modes.test_case import processing as case_processing
from exactly_lib.processing import test_case_processing
from exactly_lib.test_case import error_description
from exactly_lib.test_suite import reporting
from exactly_lib.test_suite import structure
from exactly_lib.test_suite.enumeration import SuiteEnumerator
from exactly_lib.test_suite.instruction_set.parse import SuiteReadError
from exactly_lib.test_suite.suite_hierarchy_reading import SuiteHierarchyReader
from exactly_lib.util.std import StdOutputFiles, FilePrinter


class Executor:
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
        self._reporter = self._reporter_factory.new_reporter(output, suite_root_file_path)

    def execute(self) -> int:
        final_result_output_file = FilePrinter(self._std.err)
        exit_identifier_output_file = FilePrinter(self._std.out)
        exit_value = self._execute_and_let_reporter_report_final_result(final_result_output_file)
        self._std.err.flush()
        exit_identifier_output_file.write_line(exit_value.exit_identifier)
        return exit_value.exit_code

    def _execute_and_let_reporter_report_final_result(self,
                                                      reporter_out: FilePrinter) -> ExitValue:
        try:
            root_suite = self._read_structure(self._suite_root_file_path)
            suits_in_processing_order = self._suite_enumerator.apply(root_suite)
            self._process_suits(suits_in_processing_order)
            return self._reporter.report_final_results_for_valid_suite(reporter_out)
        except SuiteReadError as ex:
            file_printer = FilePrinter(self._std.err)
            output_location(file_printer,
                            ex.suite_file,
                            ex.maybe_section_name,
                            ex.line,
                            'section')
            file_printer.write_lines(ex.error_message_lines())

            return self._reporter.report_final_results_for_invalid_suite(reporter_out)

    def _read_structure(self,
                        suite_file_path: pathlib.Path) -> structure.TestSuite:
        return self._suite_hierarchy_reader.apply(suite_file_path)

    def _process_suits(self,
                       suits_in_processing_order: list):
        """
        :param suits_in_processing_order: [TestSuite]
        :return: Exit code from main program.
        """
        self._reporter.root_suite_begin()
        for suite in suits_in_processing_order:
            self._process_single_sub_suite(suite)
        self._reporter.root_suite_end()

    def _process_single_sub_suite(self,
                                  suite: structure.TestSuite):
        """
        Executes a single suite (i.e. not it's sub suites).
        """
        sub_suite_reporter = self._reporter.new_sub_suite_reporter(suite)
        sub_suite_reporter.listener().suite_begin()
        configuration = self._configuration_for_cases_in_suite(suite)
        case_processor = self._test_case_processor_constructor(configuration)
        for case in suite.test_cases:
            sub_suite_reporter.listener().case_begin(case)
            result = self._process_case(case_processor, case)
            sub_suite_reporter.listener().case_end(case,
                                                   result)
            sub_suite_reporter.case_end(case,
                                        result)
        sub_suite_reporter.listener().suite_end()
        pass

    @staticmethod
    def _process_case(case_processor: test_case_processing.Processor,
                      case: test_case_processing.TestCaseSetup) -> test_case_processing.Result:
        try:
            return case_processor.apply(case)
        except Exception as ex:
            error_info = test_case_processing.ErrorInfo(error_description.of_exception(ex),
                                                        file_path=case.file_path)
            return test_case_processing.new_internal_error(error_info)

    def _configuration_for_cases_in_suite(self, suite: structure.TestSuite) -> case_processing.Configuration:
        return case_processing.Configuration(
            self._default_case_configuration.split_line_into_name_and_argument_function,
            self._default_case_configuration.instruction_setup,
            suite.test_case_handling_setup,
            self._default_case_configuration.is_keep_execution_directory_root,
            self._default_case_configuration.execution_directory_root_name_prefix)
