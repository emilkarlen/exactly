import pathlib

from shellcheck_lib.cli.execution_mode.test_suite import settings
from shellcheck_lib.execution.result import FullResult
from shellcheck_lib.general.output import StdOutputFiles
from shellcheck_lib.test_suite import structure
from shellcheck_lib.test_suite.suite_hierarchy_reading import SuiteHierarchyReader


class SuiteStructureError(Exception):
    pass


class Executor:
    def __init__(self,
                 output: StdOutputFiles,
                 suite_hierarchy_reader: SuiteHierarchyReader,
                 execution_settings: settings.Settings):
        self._std = output
        self._suite_hierarchy_reader = suite_hierarchy_reader
        self._execution_settings = execution_settings
        self._reporter = execution_settings.reporter_factory.new_reporter(output)

    def execute(self) -> int:
        try:
            root_suite = self._read_structure(self._execution_settings.suite_root_file_path)
            suits_in_execution_order = self._execution_settings.suite_enumerator.apply(root_suite)
            exit_code = self._execute_suits_and_cases(suits_in_execution_order)
            return exit_code
        except SuiteStructureError:
            exit_code = self._reporter.invalid_suite_exit_code()
            return exit_code

    def _read_structure(self,
                        suite_file_path: pathlib.Path) -> structure.TestSuite:
        return structure.TestSuite([], [])

    def _execute_suits_and_cases(self,
                                 suits_in_execution_order: list) -> int:
        """
        :param suits_in_execution_order: [TestSuite]
        :return: Exit code from main program.
        """
        for suite in suits_in_execution_order:
            self._execute_single_sub_suite(suite)
        return 1

    def _execute_single_sub_suite(self,
                                  suite: structure.TestSuite):
        """
        Executes a single suite (i.e. not it's sub suites).
        """
        sub_suite_reporter = self._reporter.new_sub_suite_reporter(suite)
        sub_suite_reporter.suite_begin()
        for case in suite.test_cases:
            sub_suite_reporter.case_begin(case)
            full_result = self._execute_full_case(case)
            sub_suite_reporter.case_end(case,
                                        full_result)
        sub_suite_reporter.suite_end()
        pass

    def _execute_full_case(self,
                           case: structure.TestCase) -> FullResult:
        raise NotImplementedError()
