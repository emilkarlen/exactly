import datetime
import os
import pathlib

from shellcheck_lib.cli.cli_environment.program_modes.test_case import exit_values as test_case_exit_values
from shellcheck_lib.cli.cli_environment.program_modes.test_suite import exit_values
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.test_case import test_case_processing
from shellcheck_lib.test_case.test_case_processing import Status
from shellcheck_lib.test_suite import reporting, structure
from shellcheck_lib.util.std import StdOutputFiles, FilePrinter
from shellcheck_lib.util.timedelta_format import elapsed_time_value_and_unit

SUCCESS_STATUSES = {FullResultStatus.PASS,
                    FullResultStatus.SKIPPED,
                    FullResultStatus.XFAIL
                    }


class DefaultSubSuiteProgressReporter(reporting.SubSuiteProgressReporter):
    def __init__(self,
                 output_file: FilePrinter,
                 suite: structure.TestSuite,
                 root_suite_dir_abs_path: pathlib.Path):
        self.output_file = output_file
        self.suite = suite
        self.root_suite_dir_abs_path = root_suite_dir_abs_path

    def suite_begin(self):
        self.output_file.write_line('suite ' + self._file_path_pres(self.suite.source_file) + ': begin')

    def suite_end(self):
        self.output_file.write_line('suite ' + self._file_path_pres(self.suite.source_file) + ': end')

    def case_begin(self, case: test_case_processing.TestCaseSetup):
        self.output_file.write('case  ' + self._file_path_pres(case.file_path) + ': ')

    def case_end(self,
                 case: test_case_processing.TestCaseSetup,
                 result: test_case_processing.Result):
        exit_value = test_case_exit_values.from_result(result)
        self.output_file.write_line(exit_value.exit_identifier)

    def _file_path_pres(self, file: pathlib.Path):
        try:
            return str(file.relative_to(self.root_suite_dir_abs_path))
        except ValueError:
            return str(file)


class DefaultRootSuiteReporterFactory(reporting.RootSuiteReporterFactory):
    def new_reporter(self,
                     std_output_files: StdOutputFiles,
                     root_suite_file: pathlib.Path) -> reporting.RootSuiteReporter:
        root_suite_dir_abs_path = root_suite_file.resolve().parent
        return DefaultRootSuiteReporter(std_output_files,
                                        root_suite_dir_abs_path)


class DefaultRootSuiteReporter(reporting.RootSuiteReporter):
    def __init__(self,
                 std_output_files: StdOutputFiles,
                 root_suite_dir_abs_path: pathlib.Path):
        self._output_file = FilePrinter(std_output_files.out)
        self._sub_reporters = []
        self._start_time = None
        self._total_time_timedelta = None
        self._root_suite_dir_abs_path = root_suite_dir_abs_path

    def root_suite_begin(self):
        self._start_time = datetime.datetime.now()

    def root_suite_end(self):
        stop_time = datetime.datetime.now()
        self._total_time_timedelta = stop_time - self._start_time
        pass

    def new_sub_suite_reporter(self,
                               sub_suite: structure.TestSuite) -> reporting.SubSuiteReporter:
        progress_reporter = DefaultSubSuiteProgressReporter(self._output_file,
                                                            sub_suite,
                                                            self._root_suite_dir_abs_path)
        reporter = reporting.SubSuiteReporter(progress_reporter)
        self._sub_reporters.append(reporter)
        return reporter

    def report_final_results_for_invalid_suite(self, text_output_file: FilePrinter) -> exit_values.ExitValue:
        return exit_values.INVALID_SUITE

    def report_final_results_for_valid_suite(self, text_output_file: FilePrinter) -> exit_values.ExitValue:
        num_cases, errors, exit_value = self._valid_suite_exit_value()
        lines = format_final_result_for_valid_suite(num_cases, self._total_time_timedelta, errors)
        lines.insert(0, '')
        text_output_file.write_line(os.linesep.join(lines))
        return exit_value

    def _valid_suite_exit_value(self) -> (int, dict, exit_values.ExitValue):
        errors = {}

        def add_error(exit_value: exit_values.ExitValue):
            identifier = exit_value.exit_identifier
            current = errors.setdefault(identifier, 0)
            errors[identifier] = current + 1

        num_tests = 0
        exit_value = exit_values.ALL_PASS
        for suite_reporter in self._sub_reporters:
            assert isinstance(suite_reporter, reporting.SubSuiteReporter)
            for case, result in suite_reporter.result():
                num_tests += 1
                case_exit_value = test_case_exit_values.from_result(result)
                if result.status is not Status.EXECUTED:
                    exit_value = exit_values.FAILED_TESTS
                    add_error(case_exit_value)
                elif result.execution_result.status not in SUCCESS_STATUSES:
                    exit_value = exit_values.FAILED_TESTS
                    add_error(case_exit_value)
        return num_tests, errors, exit_value


def format_final_result_for_valid_suite(num_cases: int,
                                        elapsed_time: datetime.timedelta,
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
    return ret_val
