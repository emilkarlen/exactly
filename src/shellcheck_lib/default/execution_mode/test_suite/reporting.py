import os

from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.general.std import StdOutputFiles
from shellcheck_lib.test_case import test_case_processing
from shellcheck_lib.test_suite import reporting, structure

INVALID_SUITE_EXIT_CODE = 3
FAILED_TESTS_EXIT_CODE = 4

SUCCESS_STATUSES = {FullResultStatus.PASS,
                    FullResultStatus.SKIPPED,
                    FullResultStatus.XFAIL
                    }


class ReporterFactory(reporting.ReporterFactory):
    def new_reporter(self,
                     std_output_files: StdOutputFiles) -> reporting.CompleteSuiteReporter:
        return CompleteSuiteReporter(std_output_files)


class CompleteSuiteReporter(reporting.CompleteSuiteReporter, reporting.SubSuiteReporter):
    def __init__(self,
                 std_output_files: StdOutputFiles):
        self._std_output_files = std_output_files
        self._current_suite = None
        self._exit_code = 0

    def new_sub_suite_reporter(self,
                               sub_suite: structure.TestSuite) -> reporting.SubSuiteReporter:
        self._current_suite = sub_suite
        return self

    def invalid_suite_exit_code(self) -> int:
        return INVALID_SUITE_EXIT_CODE

    def valid_suite_exit_code(self) -> int:
        return self._exit_code

    def suite_begin(self):
        self._out_line('SUITE ' + str(self._current_suite.source_file) + ': BEGIN')

    def suite_end(self):
        self._out_line('SUITE ' + str(self._current_suite.source_file) + ': END')

    def case_begin(self, case: test_case_processing.TestCaseSetup):
        self._std_output_files.out.write('CASE  ' + str(case.file_path) + ': ')

    def case_end(self,
                 case: test_case_processing.TestCaseSetup,
                 result: test_case_processing.Result):
        if result.status is not test_case_processing.Status.EXECUTED:
            self._exit_code = FAILED_TESTS_EXIT_CODE
            if result.status is test_case_processing.Status.INTERNAL_ERROR:
                self._out_line(result.status.name)
            else:
                self._out_line(result.access_error_type.name)
        else:
            status = result.execution_result.status
            self._out_line(status.name)
            if status not in SUCCESS_STATUSES:
                self._exit_code = FAILED_TESTS_EXIT_CODE

    def _out_line(self, s: str):
        self._std_output_files.out.write(s)
        self._std_output_files.out.write(os.linesep)
