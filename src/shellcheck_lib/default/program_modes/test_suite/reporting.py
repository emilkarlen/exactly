import os

import datetime

from shellcheck_lib.cli.cli_environment.program_modes.test_suite import exit_values
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.test_case import test_case_processing
from shellcheck_lib.test_case.test_case_processing import Status
from shellcheck_lib.test_suite import reporting, structure
from shellcheck_lib.util.std import StdOutputFiles
from shellcheck_lib.util.timedelta_format import elapsed_time_value_and_unit

SUCCESS_STATUSES = {FullResultStatus.PASS,
                    FullResultStatus.SKIPPED,
                    FullResultStatus.XFAIL
                    }


class DefaultSubSuiteProgressReporter(reporting.SubSuiteProgressReporter):
    def __init__(self,
                 output_file,
                 suite: structure.TestSuite):
        self.output_file = output_file
        self.suite = suite

    def suite_begin(self):
        self._write_ln('SUITE ' + str(self.suite.source_file) + ': BEGIN')

    def suite_end(self):
        self._write_ln('SUITE ' + str(self.suite.source_file) + ': END')

    def case_begin(self, case: test_case_processing.TestCaseSetup):
        self.output_file.write('CASE  ' + str(case.file_path) + ': ')

    def case_end(self,
                 case: test_case_processing.TestCaseSetup,
                 result: test_case_processing.Result):
        if result.status is not test_case_processing.Status.EXECUTED:
            if result.status is test_case_processing.Status.INTERNAL_ERROR:
                self._write_ln(result.status.name)
            else:
                self._write_ln(result.access_error_type.name)
        else:
            status = result.execution_result.status
            self._write_ln(status.name)

    def _write_ln(self, s: str):
        self.output_file.write(s)
        self.output_file.write(os.linesep)


class DefaultRootSuiteReporterFactory(reporting.RootSuiteReporterFactory):
    def new_reporter(self,
                     std_output_files: StdOutputFiles) -> reporting.RootSuiteReporter:
        return DefaultRootSuiteReporter(std_output_files)


class DefaultRootSuiteReporter(reporting.RootSuiteReporter):
    def __init__(self,
                 std_output_files: StdOutputFiles):
        self._line_printer = std_output_files.out
        self._sub_reporters = []
        self._start_time = None
        self._total_time_timedelta = None

    def root_suite_begin(self):
        self._start_time = datetime.datetime.now()

    def root_suite_end(self):
        stop_time = datetime.datetime.now()
        self._total_time_timedelta = stop_time - self._start_time
        pass

    def new_sub_suite_reporter(self,
                               sub_suite: structure.TestSuite) -> reporting.SubSuiteReporter:
        reporter = reporting.SubSuiteReporter(DefaultSubSuiteProgressReporter(self._line_printer, sub_suite))
        self._sub_reporters.append(reporter)
        return reporter

    def report_final_results_for_invalid_suite(self) -> int:
        return self._print_and_return_exit_code(exit_values.INVALID_SUITE)

    def report_final_results_for_valid_suite(self) -> int:
        num_cases, exit_value = self._valid_suite_exit_value()
        self._line_printer.write(os.linesep)
        num_tests_line = self._num_tests_line(num_cases)
        self._print_line(num_tests_line)
        return self._print_and_return_exit_code(exit_value)

    def _num_tests_line(self, num_cases: int) -> str:
        ret_val = ['Ran']
        num_tests = '1 test' if num_cases == 1 else '%d tests' % num_cases
        ret_val.append(num_tests)
        ret_val.append('in')
        ret_val.extend(self._elapsed_time_str())
        return ' '.join(ret_val)

    def _elapsed_time_str(self) -> list:
        return list(elapsed_time_value_and_unit(self._total_time_timedelta))

    def _valid_suite_exit_value(self) -> (int, exit_values.ExitValue):
        num_tests = 0
        exit_value = exit_values.ALL_PASS
        for suite_reporter in self._sub_reporters:
            assert isinstance(suite_reporter, reporting.SubSuiteReporter)
            for case, result in suite_reporter.result():
                num_tests += 1
                if result.status is not Status.EXECUTED:
                    exit_value = exit_values.FAILED_TESTS
                elif result.execution_result.status not in SUCCESS_STATUSES:
                    exit_value = exit_values.FAILED_TESTS
        return num_tests, exit_value

    def _print_and_return_exit_code(self, exit_value: exit_values.ExitValue) -> int:
        self._line_printer.write(os.linesep)
        self._print_line(exit_value.exit_identifier)
        return exit_value.exit_code

    def _print_line(self, s):
        self._line_printer.write(s)
        self._line_printer.write(os.linesep)
