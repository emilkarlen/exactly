import datetime
import os
import pathlib
from xml.etree import ElementTree as ET

from exactly_lib.execution.result import FullResultStatus
from exactly_lib.execution.result_reporting import error_message_for_full_result, error_message_for_error_info
from exactly_lib.processing.test_case_processing import Status, TestCaseSetup, Result
from exactly_lib.test_suite import reporting, structure
from exactly_lib.test_suite.reporters import simple_progress_reporter as simple_reporter
from exactly_lib.test_suite.reporting import TestCaseProcessingInfo
from exactly_lib.util.std import StdOutputFiles, FilePrinter

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
                     root_suite: structure.TestSuite,
                     std_output_files: StdOutputFiles,
                     root_suite_file: pathlib.Path) -> reporting.RootSuiteReporter:
        root_suite_dir_abs_path = root_suite_file.resolve().parent
        return JUnitRootSuiteReporter(root_suite, std_output_files, root_suite_dir_abs_path)


class JUnitRootSuiteReporter(reporting.RootSuiteReporter):
    def __init__(self,
                 root_suite: structure.TestSuite,
                 std_output_files: StdOutputFiles,
                 root_suite_dir_abs_path: pathlib.Path):
        self._root_suite = root_suite
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
            xml = ET.ElementTree(self._xml_for_suite(self._sub_reporters[0]))
        else:
            xml = ET.ElementTree(self._xml_for_suites(self._root_suite, self._sub_reporters))
        xml.write(self._std_output_files.out,
                  encoding='unicode',
                  xml_declaration=True,
                  short_empty_elements=True)
        self._std_output_files.out.write(os.linesep)
        return 0

    def _xml_for_suites(self, root_suite: structure.TestSuite, suite_reporters: list) -> ET.Element:
        def is_root_suite_and_should_skip_root_suite(reporter: reporting.SubSuiteReporter) -> bool:
            return reporter.suite is root_suite and (not root_suite.test_cases)

        root = ET.Element('testsuites')
        next_suite_id = 1
        for suite_reporter in suite_reporters:
            if not is_root_suite_and_should_skip_root_suite(suite_reporter):
                root.append(self._xml_for_suite(suite_reporter, {
                    'id': str(next_suite_id),
                    'package': str(root_suite.source_file),
                }))
                next_suite_id += 1
        return root

    def _xml_for_suite(self, suite_reporter: reporting.SubSuiteReporter,
                       additional_attributes: dict = None) -> ET.Element:
        attributes = {
            'name': self._file_path_pres(suite_reporter.suite.source_file),
            'tests': str(len(suite_reporter.result()))
        }
        if additional_attributes:
            attributes.update(additional_attributes)
        root = ET.Element('testsuite', attributes)
        num_errors = 0
        num_failures = 0
        sum_of_time_for_cases = datetime.timedelta()
        for test_case_setup, processing_info in suite_reporter.result():
            sum_of_time_for_cases += processing_info.duration
            result = processing_info.result
            root.append(self._xml_for_case(test_case_setup, processing_info))
            if result.status != Status.EXECUTED:
                num_errors += 1
            elif result.execution_result.status in FAIL_STATUSES:
                num_failures += 1
            elif result.execution_result.status in ERROR_STATUSES:
                num_errors += 1
        root.set('failures', str(num_failures))
        root.set('errors', str(num_errors))
        root.set('time', '%f' % sum_of_time_for_cases.total_seconds())
        return root

    def _xml_for_case(self, test_case_setup: TestCaseSetup, processing_info: TestCaseProcessingInfo) -> ET.Element:
        ret_val = ET.Element('testcase', {
            'name': self._file_path_pres(test_case_setup.file_path)
        })
        result = processing_info.result
        if result.status != Status.EXECUTED or result.execution_result.status in ERROR_STATUSES:
            ret_val.append(_xml_for_error(result))
        elif result.execution_result.status in FAIL_STATUSES:
            ret_val.append(_xml_for_failure(result))
        return ret_val

    def _file_path_pres(self, file: pathlib.Path):
        try:
            return str(file.relative_to(self._root_suite_dir_abs_path))
        except ValueError:
            return str(file)


def _xml_for_failure(result: Result) -> ET.Element:
    ret_val = ET.Element('failure', {
        'type': _error_type(result),
    })
    ret_val.text = _error_message_for(result)
    return ret_val


def _xml_for_error(result: Result) -> ET.Element:
    ret_val = ET.Element('error', {
        'type': _error_type(result),
    })
    ret_val.text = _error_message_for(result)
    return ret_val


def _error_message_for(result: Result) -> str:
    if result.status != Status.EXECUTED:
        return error_message_for_error_info(result.error_info)
    else:
        return error_message_for_full_result(result.execution_result)


def _error_type(result: Result) -> str:
    if result.status is Status.INTERNAL_ERROR:
        return Status.INTERNAL_ERROR.name
    elif result.status is Status.ACCESS_ERROR:
        return result.access_error_type.name
    else:
        return result.execution_result.status.name
