import pathlib

from shellcheck_lib.default.program_modes.test_case import processing as case_processing
from shellcheck_lib.test_case import error_description
from shellcheck_lib.test_case import test_case_processing
from shellcheck_lib.test_suite import reporting
from shellcheck_lib.test_suite import structure
from shellcheck_lib.test_suite.enumeration import SuiteEnumerator
from shellcheck_lib.test_suite.instruction_set.parse import SuiteReadError
from shellcheck_lib.test_suite.suite_hierarchy_reading import SuiteHierarchyReader
from shellcheck_lib.util.std import StdOutputFiles


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
        :param test_case_processor_constructor: case_processing.Configuration -> test_case_processing.Processor
        """
        self._default_case_configuration = default_case_configuration
        self._std = output
        self._suite_hierarchy_reader = suite_hierarchy_reader
        self._suite_enumerator = suite_enumerator
        self._reporter_factory = reporter_factory
        self._test_case_processor_constructor = test_case_processor_constructor
        self._suite_root_file_path = suite_root_file_path
        self._reporter = self._reporter_factory.new_reporter(output)

    def execute(self) -> int:
        try:
            root_suite = self._read_structure(self._suite_root_file_path)
            suits_in_processing_order = self._suite_enumerator.apply(root_suite)
            exit_code = self._process_suits(suits_in_processing_order)
            return exit_code
        except SuiteReadError:
            exit_code = self._reporter.report_final_results_for_invalid_suite()
            return exit_code

    def _read_structure(self,
                        suite_file_path: pathlib.Path) -> structure.TestSuite:
        return self._suite_hierarchy_reader.apply(suite_file_path)

    def _process_suits(self,
                       suits_in_processing_order: list) -> int:
        """
        :param suits_in_processing_order: [TestSuite]
        :return: Exit code from main program.
        """
        for suite in suits_in_processing_order:
            self._process_single_sub_suite(suite)
        return self._reporter.report_final_results_for_valid_suite()

    def _process_single_sub_suite(self,
                                  suite: structure.TestSuite):
        """
        Executes a single suite (i.e. not it's sub suites).
        """
        sub_suite_reporter = self._reporter.new_sub_suite_reporter(suite)
        sub_suite_reporter.listener().suite_begin()
        configuration = self.configuration_for_cases_in_suite(suite)
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

    def configuration_for_cases_in_suite(self, suite):
        return case_processing.Configuration(
            self._default_case_configuration.split_line_into_name_and_argument_function,
            self._default_case_configuration.instruction_setup,
            self._default_case_configuration.act_phase_setup,
            suite.preprocessor,
            self._default_case_configuration.is_keep_execution_directory_root,
            self._default_case_configuration.execution_directory_root_name_prefix)
