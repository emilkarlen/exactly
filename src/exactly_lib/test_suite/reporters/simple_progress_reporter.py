import datetime
import os
import pathlib

from exactly_lib.execution.result import FullResultStatus
from exactly_lib.processing import test_case_processing, exit_values as test_case_exit_values
from exactly_lib.processing.test_case_processing import Status
from exactly_lib.test_suite import reporting, structure, exit_values
from exactly_lib.test_suite.reporting import TestCaseProcessingInfo
from exactly_lib.util.std import StdOutputFiles, FilePrinter
from exactly_lib.util.timedelta_format import elapsed_time_value_and_unit

SUCCESS_STATUSES = {FullResultStatus.PASS,
                    FullResultStatus.SKIPPED,
                    FullResultStatus.XFAIL
                    }


class SimpleProgressSubSuiteProgressReporter(reporting.SubSuiteProgressReporter):
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
                 processing_info: TestCaseProcessingInfo):
        exit_value = test_case_exit_values.from_result(processing_info.result)
        self.output_file.write('(%fs) ' % processing_info.duration.total_seconds())
        self.output_file.write_line(exit_value.exit_identifier)

    def _file_path_pres(self, file: pathlib.Path):
        try:
            return str(file.relative_to(self.root_suite_dir_abs_path))
        except ValueError:
            return str(file)


class SimpleProgressRootSuiteReporterFactory(reporting.RootSuiteReporterFactory):
    def new_reporter(self,
                     root_suite: structure.TestSuite,
                     std_output_files: StdOutputFiles,
                     root_suite_file: pathlib.Path) -> reporting.RootSuiteReporter:
        root_suite_dir_abs_path = root_suite_file.resolve().parent
        return SimpleProgressRootSuiteReporter(std_output_files,
                                               root_suite_dir_abs_path)


class SimpleProgressRootSuiteReporter(reporting.RootSuiteReporter):
    def __init__(self,
                 std_output_files: StdOutputFiles,
                 root_suite_dir_abs_path: pathlib.Path):
        self._std_output_files = std_output_files
        self._output_file = FilePrinter(std_output_files.out)
        self._error_file = FilePrinter(std_output_files.err)
        self._sub_reporters = []
        self._start_time = None
        self._total_time_timedelta = None
        self._root_suite_dir_abs_path = root_suite_dir_abs_path

    def root_suite_begin(self):
        self._start_time = datetime.datetime.now()

    def root_suite_end(self):
        stop_time = datetime.datetime.now()
        self._total_time_timedelta = stop_time - self._start_time

    def new_sub_suite_reporter(self,
                               sub_suite: structure.TestSuite) -> reporting.SubSuiteReporter:
        progress_reporter = SimpleProgressSubSuiteProgressReporter(self._output_file,
                                                                   sub_suite,
                                                                   self._root_suite_dir_abs_path)
        reporter = reporting.SubSuiteReporter(sub_suite, progress_reporter)
        self._sub_reporters.append(reporter)
        return reporter

    def report_final_results(self) -> int:
        num_cases, errors, exit_value = self._valid_suite_exit_value()
        lines = format_final_result_for_valid_suite(num_cases, self._total_time_timedelta, errors)
        lines.insert(0, '')
        self._error_file.write_line(os.linesep.join(lines))
        self._std_output_files.err.flush()
        self._output_file.write_line(exit_value.exit_identifier)
        return exit_value.exit_code

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
            for case, processing_info in suite_reporter.result():
                result = processing_info.result
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
        ret_val.append(''.join(elapsed_time_value_and_unit(elapsed_time)))
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
