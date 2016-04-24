import datetime
import os

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
        num_cases, errors, exit_value = self._valid_suite_exit_value()
        lines = format_final_result_for_valid_suite(num_cases,
                                                    self._total_time_timedelta,
                                                    exit_value.exit_identifier,
                                                    errors)
        self._line_printer.write(os.linesep)
        self._print_line(os.linesep.join(lines))
        return exit_value.exit_code

    def _valid_suite_exit_value(self) -> (int, dict, exit_values.ExitValue):
        errors = {}

        def add_error(identifier: str):
            current = errors.setdefault(identifier, 0)
            errors[identifier] = current + 1

        num_tests = 0
        exit_value = exit_values.ALL_PASS
        for suite_reporter in self._sub_reporters:
            assert isinstance(suite_reporter, reporting.SubSuiteReporter)
            for case, result in suite_reporter.result():
                num_tests += 1
                if result.status is not Status.EXECUTED:
                    exit_value = exit_values.FAILED_TESTS
                    add_error(result.access_error_type.name)
                elif result.execution_result.status not in SUCCESS_STATUSES:
                    exit_value = exit_values.FAILED_TESTS
                    add_error(result.execution_result.status.name)
        return num_tests, errors, exit_value

    def _print_and_return_exit_code(self, exit_value: exit_values.ExitValue) -> int:
        self._line_printer.write(os.linesep)
        self._print_line(exit_value.exit_identifier)
        return exit_value.exit_code

    def _print_line(self, s):
        self._line_printer.write(s)
        self._line_printer.write(os.linesep)


def format_final_result_for_valid_suite(num_cases: int,
                                        elapsed_time: datetime.timedelta,
                                        exit_identifier: str,
                                        errors: dict) -> list:
    """
    :return: The list of lines that should be reported.
    """

    def num_tests_line() -> str:
        ret_val = ['Ran']
        num_tests = '1 test' if num_cases == 1 else '%d tests' % num_cases
        ret_val.append(num_tests)
        ret_val.append('in')
        ret_val.extend(list(elapsed_time_value_and_unit(elapsed_time)))
        return ' '.join(ret_val)

    def error_lines() -> list:
        ret_val = []
        sorted_exit_identifiers = sorted(errors.keys())
        max_ident_len = max(map(len, sorted_exit_identifiers))
        format_str = '%-' + str(max_ident_len) + 's : %d'
        for ident in sorted_exit_identifiers:
            ret_val.append(format_str % (ident, errors[ident]))
        return ret_val

    ret_val = []
    ret_val.append(num_tests_line())
    if errors:
        ret_val.append('')
        ret_val.extend(error_lines())
    ret_val.extend(['', exit_identifier])
    return ret_val
