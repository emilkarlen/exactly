import datetime
import os
import pathlib
from xml.etree import ElementTree as ET

from exactly_lib.execution import exit_values as test_case_exit_values
from exactly_lib.execution.result import FullResultStatus
from exactly_lib.execution.result_reporting import error_message_for_full_result
from exactly_lib.processing.test_case_processing import Status, TestCaseSetup, Result
from exactly_lib.test_suite import reporting, structure, exit_values
from exactly_lib.test_suite.reporters import simple_progress_reporter as simple_reporter
from exactly_lib.util.std import StdOutputFiles, FilePrinter
from exactly_lib.util.timedelta_format import elapsed_time_value_and_unit

FAIL_STATUSES = {FullResultStatus.FAIL,
                 FullResultStatus.XPASS,
                 }

ERROR_STATUSES = {FullResultStatus.VALIDATE,
                  FullResultStatus.HARD_ERROR,
                  FullResultStatus.IMPLEMENTATION_ERROR,
                  }

NON_PASS_STATUSES = FAIL_STATUSES.union(ERROR_STATUSES)


class JUnitRootSuiteReporterFactory(reporting.RootSuiteReporterFactory):
    def new_reporter(self,
                     std_output_files: StdOutputFiles,
                     root_suite_file: pathlib.Path) -> reporting.RootSuiteReporter:
        root_suite_dir_abs_path = root_suite_file.resolve().parent
        return JUnitRootSuiteReporter(std_output_files,
                                      root_suite_dir_abs_path)


class JUnitRootSuiteReporter(reporting.RootSuiteReporter):
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
        pass

    def new_sub_suite_reporter(self,
                               sub_suite: structure.TestSuite) -> reporting.SubSuiteReporter:
        progress_reporter = simple_reporter.SimpleProgressSubSuiteProgressReporter(self._error_file,
                                                                                   sub_suite,
                                                                                   self._root_suite_dir_abs_path)
        reporter = reporting.SubSuiteReporter(sub_suite, progress_reporter)
        self._sub_reporters.append(reporter)
        return reporter

    def report_final_results(self) -> int:
        if len(self._sub_reporters) == 1:
            xml = ET.ElementTree(_xml_for_suite(self._sub_reporters[0]))
        else:
            raise NotImplementedError()
        xml.write(self._std_output_files.out,
                  encoding='unicode',
                  xml_declaration=True,
                  short_empty_elements=True)
        self._std_output_files.out.write(os.linesep)
        return 0

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


def _xml_for_suite(suite_reporter: reporting.SubSuiteReporter) -> ET.Element:
    suite_reporter.result()
    root = ET.Element('testsuite', {
        'name': str(suite_reporter.suite.source_file),
        'tests': str(len(suite_reporter.result()))
    })
    num_errors = 0
    num_failures = 0
    for test_case_setup, result in suite_reporter.result():
        root.append(_xml_for_case(test_case_setup, result))
        if result.status != Status.EXECUTED:
            num_errors += 1
        elif result.execution_result.status in FAIL_STATUSES:
            num_failures += 1
        elif result.execution_result.status in ERROR_STATUSES:
            num_errors += 1
    if num_failures > 0:
        root.set('failures', str(num_failures))
    if num_errors > 0:
        root.set('errors', str(num_errors))
    return root


def _xml_for_case(test_case_setup: TestCaseSetup, result: Result) -> ET.Element:
    ret_val = ET.Element('testcase', {
        'name': str(test_case_setup.file_path)
    })
    if result.status != Status.EXECUTED or result.execution_result.status in NON_PASS_STATUSES:
        ret_val.append(_xml_for_failure(result))
    return ret_val


def _xml_for_failure(result: Result) -> ET.Element:
    ret_val = ET.Element('failure')
    ret_val.text = _error_message_for(result)
    return ret_val


def _error_message_for(result: Result) -> str:
    if result.status != Status.EXECUTED:
        return result.access_error_type.name
    else:
        return error_message_for_full_result(result.execution_result)
