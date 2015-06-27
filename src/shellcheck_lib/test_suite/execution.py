import pathlib

from shellcheck_lib.general.output import StdOutputFiles
from shellcheck_lib.test_suite import structure
from shellcheck_lib.test_suite import reporting
from shellcheck_lib.test_suite.enumeration import SuiteEnumerator
from shellcheck_lib.test_suite.parse import SuiteReadError
from shellcheck_lib.test_suite.suite_hierarchy_reading import SuiteHierarchyReader
from shellcheck_lib.test_case import test_case_processing


class Executor:
    def __init__(self,
                 output: StdOutputFiles,
                 suite_hierarchy_reader: SuiteHierarchyReader,
                 reporter_factory: reporting.ReporterFactory,
                 suite_enumerator: SuiteEnumerator,
                 test_case_processor: test_case_processing.Processor,
                 suite_root_file_path: pathlib.Path):
        self._std = output
        self._suite_hierarchy_reader = suite_hierarchy_reader
        self._test_case_processor = test_case_processor
        self._suite_enumerator = suite_enumerator
        self._reporter_factory = reporter_factory
        self._suite_root_file_path = suite_root_file_path
        self._reporter = self._reporter_factory.new_reporter(output)

    def execute(self) -> int:
        try:
            root_suite = self._read_structure(self._suite_root_file_path)
            suits_in_processing_order = self._suite_enumerator.apply(root_suite)
            exit_code = self._process_suits(suits_in_processing_order)
            return exit_code
        except SuiteReadError:
            exit_code = self._reporter.invalid_suite_exit_code()
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
        return self._reporter.valid_suite_exit_code()

    def _process_single_sub_suite(self,
                                  suite: structure.TestSuite):
        """
        Executes a single suite (i.e. not it's sub suites).
        """
        sub_suite_reporter = self._reporter.new_sub_suite_reporter(suite)
        sub_suite_reporter.suite_begin()
        for case in suite.test_cases:
            sub_suite_reporter.case_begin(case)
            result = self._process_case(case)
            sub_suite_reporter.case_end(case,
                                        result)
        sub_suite_reporter.suite_end()
        pass

    def _process_case(self,
                      case: test_case_processing.TestCase) -> test_case_processing.Result:
        try:
            return self._test_case_processor.apply(case)
        except Exception as ex:
            return test_case_processing.new_internal_error(str(ex))
