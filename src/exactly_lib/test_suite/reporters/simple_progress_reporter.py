import datetime
import os
import pathlib
from typing import Dict, List, Tuple

from exactly_lib.common.exit_value import ExitValue
from exactly_lib.common.process_result_reporter import Environment
from exactly_lib.execution.full_execution.result import FullExeResultStatus
from exactly_lib.processing import test_case_processing, exit_values as test_case_exit_values
from exactly_lib.processing.test_case_processing import Status, TestCaseFileReference
from exactly_lib.test_suite import reporting, structure, exit_values
from exactly_lib.test_suite.reporting import TestCaseProcessingInfo
from exactly_lib.util import name
from exactly_lib.util.file_printer import FilePrinter, file_printer_with_color_if_terminal
from exactly_lib.util.std import StdOutputFiles

SUCCESS_STATUSES = {FullExeResultStatus.PASS,
                    FullExeResultStatus.SKIPPED,
                    FullExeResultStatus.XFAIL
                    }

_TIME_FORMAT = '%.3fs'
_TIME_FORMAT__CASE = '(' + _TIME_FORMAT + ') '


class SimpleProgressSubSuiteProgressReporter(reporting.SubSuiteProgressReporter):
    def __init__(self,
                 output_file: FilePrinter,
                 suite: structure.TestSuiteHierarchy,
                 root_suite_dir_abs_path: pathlib.Path):
        self.output_file = output_file
        self.suite = suite
        self._rel_path_presenter = _RelPathPresenter(root_suite_dir_abs_path)

    def suite_begin(self):
        self.output_file.write_line('suite ' + self._file_path_pres(self.suite.source_file) + ': begin')

    def suite_end(self):
        self.output_file.write_line('suite ' + self._file_path_pres(self.suite.source_file) + ': end')

    def case_begin(self, case: test_case_processing.TestCaseFileReference):
        self.output_file.write('case  ' + self._file_path_pres(case.file_path) + ': ',
                               flush=True)

    def case_end(self,
                 case: test_case_processing.TestCaseFileReference,
                 processing_info: TestCaseProcessingInfo):
        exit_value = test_case_exit_values.from_result(processing_info.result)
        self.output_file.write(_TIME_FORMAT__CASE % processing_info.duration.total_seconds())
        self.output_file.write_colored_line(exit_value.exit_identifier, exit_value.color)

    def _file_path_pres(self, file: pathlib.Path):
        return self._rel_path_presenter.present(file)


class _RelPathPresenter:
    def __init__(self, relativity_root_abs_path: pathlib.Path):
        self.relativity_root_abs_path = relativity_root_abs_path

    def present(self, file: pathlib.Path) -> str:
        try:
            return str(file.relative_to(self.relativity_root_abs_path))
        except ValueError:
            return str(file)


class SimpleProgressRootSuiteProcessingReporter(reporting.RootSuiteProcessingReporter):
    def report_invalid_suite(self,
                             exit_value: ExitValue,
                             reporting_environment: Environment,
                             ):
        reporting_environment.out_printer.write_colored_line(exit_value.exit_identifier, exit_value.color)

    def execution_reporter(self,
                           root_suite: structure.TestSuiteHierarchy,
                           reporting_environment: Environment,
                           root_suite_file: pathlib.Path) -> reporting.RootSuiteReporter:
        root_suite_dir_abs_path = root_suite_file.resolve().parent
        return SimpleProgressRootSuiteReporter(reporting_environment.std_files,
                                               root_suite_dir_abs_path)


class SimpleProgressRootSuiteReporter(reporting.RootSuiteReporter):
    def __init__(self,
                 std_output_files: StdOutputFiles,
                 root_suite_dir_abs_path: pathlib.Path):
        self._std_output_files = std_output_files
        self._output_file = file_printer_with_color_if_terminal(std_output_files.out)
        self._error_file = file_printer_with_color_if_terminal(std_output_files.err)
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
                               sub_suite: structure.TestSuiteHierarchy) -> reporting.SubSuiteReporter:
        progress_reporter = SimpleProgressSubSuiteProgressReporter(self._output_file,
                                                                   sub_suite,
                                                                   self._root_suite_dir_abs_path)
        reporter = reporting.SubSuiteReporter(sub_suite, progress_reporter)
        self._sub_reporters.append(reporter)
        return reporter

    def report_final_results(self) -> int:
        num_cases, errors, exit_value = self._valid_suite_exit_value()
        lines = format_final_result_for_valid_suite(num_cases, self._total_time_timedelta,
                                                    self._root_suite_dir_abs_path,
                                                    errors)
        self._std_output_files.out.flush()
        lines.insert(0, '')
        self._error_file.write_line(os.linesep.join(lines))
        self._std_output_files.err.flush()
        self._output_file.write_colored_line(exit_value.exit_identifier, exit_value.color)
        return exit_value.exit_code

    def _valid_suite_exit_value(self) -> Tuple[int,
                                               Dict[str, List[TestCaseFileReference]],
                                               exit_values.ExitValue]:
        errors = {}

        def add_error(exit_value: exit_values.ExitValue, case: TestCaseFileReference):
            current = errors.setdefault(exit_value.exit_identifier, [])
            current.append(case)

        num_tests = 0
        exit_value = exit_values.ALL_PASS
        for suite_reporter in self._sub_reporters:
            assert isinstance(suite_reporter, reporting.SubSuiteReporter)
            for case_setup, processing_info in suite_reporter.result():
                result = processing_info.result
                num_tests += 1
                case_exit_value = test_case_exit_values.from_result(result)
                if result.status is not Status.EXECUTED:
                    exit_value = exit_values.FAILED_TESTS
                    add_error(case_exit_value, case_setup)
                elif result.execution_result.status not in SUCCESS_STATUSES:
                    exit_value = exit_values.FAILED_TESTS
                    add_error(case_exit_value, case_setup)
        return num_tests, errors, exit_value


def format_final_result_for_valid_suite(num_cases: int,
                                        elapsed_time: datetime.timedelta,
                                        relativity_root_abs_path: pathlib.Path,
                                        errors: Dict[str, List[TestCaseFileReference]]) -> List[str]:
    """
    :return: The list of lines that should be reported.
    """
    path_presenter = _RelPathPresenter(relativity_root_abs_path)

    def num_tests_line() -> str:
        return ' '.join([
            'Ran',
            _NUMBER_OF_TESTS.of(num_cases),
            'in',
            _TIME_FORMAT % elapsed_time.total_seconds(),
        ])

    def num_unsuccessful_lines() -> List[str]:
        if not errors:
            return []
        num_failing = sum([len(cases) for cases in errors.values()])
        return [
            '',
            _NUMBER_OF_ERRORS.of(num_failing)
        ]

    def error_lines() -> List[str]:
        ret_val = []
        sorted_exit_identifiers = sorted(errors.keys())
        for exit_identifier in sorted_exit_identifiers:
            ret_val.append(exit_identifier)
            for case in errors[exit_identifier]:
                ret_val.append('  ' + path_presenter.present(case.file_path))
        return ret_val

    ret_val = [num_tests_line()]
    ret_val += num_unsuccessful_lines()
    if errors:
        ret_val.append('')
        ret_val += error_lines()
    return ret_val


_NUMBER_OF_TESTS = name.NumberOfItemsString(name.name_with_plural_s('test'))

_NUMBER_OF_ERRORS = name.NumberOfItemsString(name.name_with_plural_s('error'))
