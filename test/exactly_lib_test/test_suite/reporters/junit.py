import io
import os
import platform
import re
import unittest
from pathlib import Path
from typing import List, Dict
from xml.etree import ElementTree as ET

from exactly_lib.common.exit_value import ExitValue
from exactly_lib.common.result_reporting import error_message_for_full_result, error_message_for_error_info
from exactly_lib.processing import test_case_processing as tcp
from exactly_lib.processing.test_case_processing import Result, AccessErrorType
from exactly_lib.test_suite import processing
from exactly_lib.test_suite import structure
from exactly_lib.test_suite.reporters import junit as sut
from exactly_lib.util.ansi_terminal_color import ForegroundColor
from exactly_lib_test.execution.full_execution.test_resources.result_values import FULL_RESULT_HARD_ERROR, \
    FULL_RESULT_VALIDATE, \
    FULL_RESULT_INTERNAL_ERROR, FULL_RESULT_XPASS, FULL_RESULT_XFAIL
from exactly_lib_test.test_case.test_resources import error_info
from exactly_lib_test.test_resources.files.str_std_out_files import StringStdOutFiles
from exactly_lib_test.test_resources.value_assertions import xml_etree as asrt_etree
from exactly_lib_test.test_suite.test_resources.processing_utils import FULL_RESULT_PASS, test_suite, test_case, \
    FULL_RESULT_FAIL, FULL_RESULT_SKIP, TestCaseProcessorThatGivesConstantPerCase
from exactly_lib_test.test_suite.test_resources.processing_utils import TestCaseProcessorThatGivesConstant, \
    DUMMY_CASE_PROCESSING


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidSuite),
        unittest.makeSuite(TestExecutionOfSingleSuiteWithSingleTestCase),
        unittest.makeSuite(TestExecutionOfSingleSuiteWithMultipleTestCases),
        unittest.makeSuite(TestExecutionOfSuiteWithoutTestCasesButWithSubSuites),
        unittest.makeSuite(TestExecutionOfRootSuiteWithBothTestCasesAndSubSuites),
    ])


class TestInvalidSuite(unittest.TestCase):
    def test(self):
        # ARRANGE #
        reporter = sut.JUnitRootSuiteProcessingReporter()
        str_std_out_files = StringStdOutFiles()
        # ACT #
        reporter.report_invalid_suite(ExitValue(1, 'IDENTIFIER', ForegroundColor.BLACK),
                                      str_std_out_files.reporting_environment)
        # ASSERT #
        str_std_out_files.finish()
        self.assertEqual('',
                         str_std_out_files.stdout_contents,
                         'Output to stdout')
        self.assertEqual('',
                         str_std_out_files.stderr_contents,
                         'Output to stderr')


class TestExecutionOfSingleSuiteWithSingleTestCase(unittest.TestCase):
    def test_empty_suite(self):
        # ARRANGE #
        expected_xml = suite_xml(
            attributes={
                'name': 'root file name',
                'tests': '0',
                'errors': '0',
                'failures': '0',
            },
            test_case_elements=[],
        )
        expected__assertion = asrt_etree.str_as_xml_equals(expected_xml)

        root_suite = test_suite('root file name', [], [])
        test_suites = [root_suite]
        # ACT #
        actual = execute_with_case_processing_with_constant_result(FULL_RESULT_PASS,
                                                                   root_suite,
                                                                   Path(),
                                                                   test_suites)
        # ASSERT #
        self.assertEqual(sut.UNCONDITIONAL_EXIT_CODE, actual.exit_code)

        expected__assertion.apply_with_message(self,
                                               replace_xml_variables(actual.stdout),
                                               'suite xml on stdout')

    def test_single_case_that_passes(self):
        cases = [
            FULL_RESULT_PASS,
            FULL_RESULT_XFAIL,
            FULL_RESULT_SKIP,
        ]
        for case_result in cases:
            with self.subTest(case_result_status=case_result.status):
                # ARRANGE #
                expected_xml = suite_xml(attributes={
                    'name': 'suite that passes',
                    'tests': '1',
                    'errors': '0',
                    'failures': '0',
                },
                    test_case_elements=[successful_test_case_xml('test case file name')]
                )
                expected__assertion = asrt_etree.str_as_xml_equals(expected_xml)
                root_suite = test_suite('suite that passes', [], [test_case('test case file name')])
                test_suites = [root_suite]
                # ACT #
                actual = execute_with_case_processing_with_constant_result(
                    tcp.new_executed(case_result),
                    root_suite,
                    Path(),
                    test_suites)

                # ASSERT #
                self.assertEqual(sut.UNCONDITIONAL_EXIT_CODE, actual.exit_code)
                expected__assertion.apply_with_message(self,
                                                       replace_xml_variables(actual.stdout),
                                                       'suite xml on stdout')

    def test_single_case_with_error(self):
        cases = [
            FULL_RESULT_HARD_ERROR,
            FULL_RESULT_VALIDATE,
            FULL_RESULT_INTERNAL_ERROR,
        ]
        for case_result in cases:
            with self.subTest(case_result_status=case_result.status):
                # ARRANGE #
                expected_xml = suite_xml(attributes={
                    'name': 'suite with error',
                    'tests': '1',
                    'errors': '1',
                    'failures': '0'},
                    test_case_elements=[
                        erroneous_test_case_xml('test case file name',
                                                error_type=case_result.status.name,
                                                failure_message=error_message_for_full_result(case_result))])
                expected__assertion = asrt_etree.str_as_xml_equals(expected_xml)
                root_suite = test_suite('suite with error', [], [test_case('test case file name')])
                test_suites = [root_suite]
                # ACT #
                actual = execute_with_case_processing_with_constant_result(
                    tcp.new_executed(case_result),
                    root_suite,
                    Path(),
                    test_suites)

                # ASSERT #
                self.assertEqual(sut.UNCONDITIONAL_EXIT_CODE, actual.exit_code)
                expected__assertion.apply_with_message(self,
                                                       replace_xml_variables(actual.stdout),
                                                       'suite xml on stdout')

    def test_single_case_with_error_due_to_failure_to_execute(self):
        cases = [
            (tcp.new_internal_error(error_info.of_message('error message')),
             tcp.Status.INTERNAL_ERROR.name),
            (tcp.new_access_error(AccessErrorType.FILE_ACCESS_ERROR,
                                  error_info.of_message('error message')),
             AccessErrorType.FILE_ACCESS_ERROR.name),
        ]
        for case_result, error_type in cases:
            with self.subTest(case_result_status=case_result.status):
                # ARRANGE #
                expected_xml = suite_xml(attributes={
                    'name': 'suite with error',
                    'tests': '1',
                    'errors': '1',
                    'failures': '0'},
                    test_case_elements=[
                        erroneous_test_case_xml('test case file name',
                                                error_type=error_type,
                                                failure_message=error_message_for_error_info(case_result.error_info))
                    ])
                expected__assertion = asrt_etree.str_as_xml_equals(expected_xml)
                root_suite = test_suite('suite with error', [], [test_case('test case file name')])
                test_suites = [root_suite]
                # ACT #
                actual = execute_with_case_processing_with_constant_result(
                    case_result,
                    root_suite,
                    Path(),
                    test_suites)

                # ASSERT #
                self.assertEqual(sut.UNCONDITIONAL_EXIT_CODE, actual.exit_code)
                expected__assertion.apply_with_message(self,
                                                       replace_xml_variables(actual.stdout),
                                                       'suite xml on stdout')

    def test_single_case_with_failure(self):
        cases = [
            FULL_RESULT_FAIL,
            FULL_RESULT_XPASS,
        ]
        for case_result in cases:
            with self.subTest(case_result_status=case_result.status):
                # ARRANGE #
                expected_xml = suite_xml(attributes={
                    'name': 'suite with failure',
                    'tests': '1',
                    'errors': '0',
                    'failures': '1'},
                    test_case_elements=[
                        failing_test_case_xml('test case file name',
                                              failure_type=case_result.status.name,
                                              failure_message=error_message_for_full_result(case_result))
                    ])
                expected__assertion = asrt_etree.str_as_xml_equals(expected_xml)
                root_suite = test_suite('suite with failure', [], [test_case('test case file name')])
                test_suites = [root_suite]
                # ACT #
                actual = execute_with_case_processing_with_constant_result(
                    tcp.new_executed(case_result),
                    root_suite,
                    Path(),
                    test_suites)
                # ASSERT #
                self.assertEqual(sut.UNCONDITIONAL_EXIT_CODE, actual.exit_code)
                expected__assertion.apply_with_message(self,
                                                       replace_xml_variables(actual.stdout),
                                                       'suite xml on stdout')


class TestExecutionOfSingleSuiteWithMultipleTestCases(unittest.TestCase):
    def test_single_sub_suite_with_test_cases_with_different_results(self):
        # ARRANGE #
        tc_pass = test_case('successful case')
        tc_fail = test_case('failing case')
        tc_error = test_case('erroneous case')
        root_suite = test_suite('suite file name', [], [
            tc_pass,
            tc_fail,
            tc_error,
        ])
        suites = [root_suite]
        test_case_processor = TestCaseProcessorThatGivesConstantPerCase({
            id(tc_pass): tcp.new_executed(FULL_RESULT_PASS),
            id(tc_fail): tcp.new_executed(FULL_RESULT_FAIL),
            id(tc_error): tcp.new_executed(FULL_RESULT_HARD_ERROR),
        })
        # ACT #
        actual = execute_with_case_processing_with_constant_processor(test_case_processor,
                                                                      root_suite,
                                                                      Path(),
                                                                      suites)
        # ASSERT #
        expected_xml = suite_xml(attributes={
            'name': 'suite file name',
            'tests': '3',
            'errors': '1',
            'failures': '1',
        },
            test_case_elements=[
                successful_test_case_xml('successful case'),
                failing_test_case_xml('failing case',
                                      failure_type=FULL_RESULT_FAIL.status.name,
                                      failure_message=error_message_for_full_result(FULL_RESULT_FAIL)),
                erroneous_test_case_xml('erroneous case',
                                        error_type=FULL_RESULT_HARD_ERROR.status.name,
                                        failure_message=error_message_for_full_result(FULL_RESULT_HARD_ERROR)),
            ]
        )
        expected__assertion = asrt_etree.str_as_xml_equals(expected_xml)
        self.assertEqual(sut.UNCONDITIONAL_EXIT_CODE, actual.exit_code)
        expected__assertion.apply_with_message(self,
                                               replace_xml_variables(actual.stdout),
                                               'suite xml on stdout')


class TestExecutionOfSuiteWithoutTestCasesButWithSubSuites(unittest.TestCase):
    def test_suite_with_only_single_sub_suite_SHOULD_not_include_root_suite_as_test_suite(self):
        # ARRANGE #
        suite_with_single_case = test_suite('suite with single case', [], [
            test_case('the test case')
        ])
        root_suite = test_suite('root suite file name', [
            suite_with_single_case,
        ], [])
        suites = [
            root_suite,
            suite_with_single_case,
        ]
        # ACT #
        actual = execute_with_case_processing_with_constant_result(tcp.new_executed(FULL_RESULT_PASS),
                                                                   root_suite,
                                                                   Path(),
                                                                   suites)
        # ASSERT #
        expected_xml = _suites_xml([
            suite_xml(attributes={
                'name': 'suite with single case',
                'package': '.',
                'id': '1',
                'tests': '1',
                'errors': '0',
                'failures': '0',
            },
                test_case_elements=[successful_test_case_xml('the test case')]
            ),
        ])
        expected__assertion = asrt_etree.str_as_xml_equals(expected_xml)
        self.assertEqual(sut.UNCONDITIONAL_EXIT_CODE, actual.exit_code)
        expected__assertion.apply_with_message(self,
                                               replace_xml_variables(actual.stdout),
                                               'suite xml on stdout')

    def test_suite_with_sub_suites_with_successful_and_non_successful_cases(self):
        # ARRANGE #
        tc_pass = test_case('successful case')
        tc_fail = test_case('failing case')
        tc_error = test_case('erroneous case')
        suite_with_single_successful_case = test_suite('suite with single successful case', [], [tc_pass])
        suite_with_failing_and_erroneous_case = test_suite('suite with failing and erroneous case', [], [
            tc_fail, tc_error
        ])
        root_suite = test_suite('root suite file name', [
            suite_with_single_successful_case,
            suite_with_failing_and_erroneous_case,
        ], [])
        suites = [
            root_suite,
            suite_with_single_successful_case,
            suite_with_failing_and_erroneous_case,
        ]
        test_case_processor = TestCaseProcessorThatGivesConstantPerCase({
            id(tc_pass): tcp.new_executed(FULL_RESULT_PASS),
            id(tc_fail): tcp.new_executed(FULL_RESULT_FAIL),
            id(tc_error): tcp.new_executed(FULL_RESULT_HARD_ERROR),
        })
        # ACT #
        actual = execute_with_case_processing_with_constant_processor(test_case_processor,
                                                                      root_suite,
                                                                      Path(),
                                                                      suites)
        # ASSERT #
        expected_xml = _suites_xml([
            suite_xml(attributes={
                'name': 'suite with single successful case',
                'package': '.',
                'id': '1',
                'tests': '1',
                'errors': '0',
                'failures': '0',
            },
                test_case_elements=[successful_test_case_xml('successful case')]
            ),
            suite_xml(attributes={
                'name': 'suite with failing and erroneous case',
                'package': '.',
                'id': '2',
                'tests': '2',
                'errors': '1',
                'failures': '1',
            },
                test_case_elements=[
                    failing_test_case_xml('failing case',
                                          failure_type=FULL_RESULT_FAIL.status.name,
                                          failure_message=error_message_for_full_result(FULL_RESULT_FAIL)),
                    erroneous_test_case_xml('erroneous case',
                                            error_type=FULL_RESULT_HARD_ERROR.status.name,
                                            failure_message=error_message_for_full_result(FULL_RESULT_HARD_ERROR)),
                ]
            ),
        ])
        expected__assertion = asrt_etree.str_as_xml_equals(expected_xml)
        self.assertEqual(sut.UNCONDITIONAL_EXIT_CODE, actual.exit_code)
        expected__assertion.apply_with_message(self, replace_xml_variables(actual.stdout),
                                               'suite xml on stdout')


class TestExecutionOfRootSuiteWithBothTestCasesAndSubSuites(unittest.TestCase):
    def test_suite_with_only_single_sub_suite_SHOULD_not_include_root_suite_as_test_suite(self):
        # ARRANGE #
        suite_with_single_case = test_suite('suite with single case', [], [
            test_case('test case in sub suite'),
        ])
        root_suite = test_suite('root suite file name',
                                [suite_with_single_case],
                                [test_case('test case in root suite')])
        suites = [
            root_suite,
            suite_with_single_case,
        ]
        # ACT #
        actual = execute_with_case_processing_with_constant_result(tcp.new_executed(FULL_RESULT_PASS),
                                                                   root_suite,
                                                                   Path(),
                                                                   suites)
        # ASSERT #
        expected_xml = _suites_xml([
            suite_xml(attributes={
                'name': 'root suite file name',
                'package': '.',
                'id': '1',
                'tests': '1',
                'errors': '0',
                'failures': '0',
            },
                test_case_elements=[successful_test_case_xml('test case in root suite')]
            ),
            suite_xml(attributes={
                'name': 'suite with single case',
                'package': '.',
                'id': '2',
                'tests': '1',
                'errors': '0',
                'failures': '0',
            },
                test_case_elements=[successful_test_case_xml('test case in sub suite')]
            ),
        ])
        expected__assertion = asrt_etree.str_as_xml_equals(expected_xml)
        self.assertEqual(sut.UNCONDITIONAL_EXIT_CODE, actual.exit_code)
        expected__assertion.apply_with_message(self,
                                               replace_xml_variables(actual.stdout),
                                               'suite xml on stdout')


class ExitCodeAndStdOut(tuple):
    def __new__(cls,
                exit_code: int,
                stdout: str):
        return tuple.__new__(cls, (exit_code, stdout))

    @property
    def exit_code(self) -> int:
        return self[0]

    @property
    def stdout(self) -> str:
        return self[1]


def execute_with_case_processing_with_constant_result(case_result: Result,
                                                      root_suite: structure.TestSuiteHierarchy,
                                                      root_file_path: Path,
                                                      test_suites: list) -> ExitCodeAndStdOut:
    return execute_with_case_processing_with_constant_processor(TestCaseProcessorThatGivesConstant(case_result),
                                                                root_suite,
                                                                root_file_path,
                                                                test_suites)


def execute_with_case_processing_with_constant_processor(processor: tcp.Processor,
                                                         root_suite: structure.TestSuiteHierarchy,
                                                         root_file_path: Path,
                                                         test_suites: list) -> ExitCodeAndStdOut:
    std_output_files = StringStdOutFiles()
    reporter = sut.JUnitRootSuiteProcessingReporter()
    execution_reporter = reporter.execution_reporter(root_suite,
                                                     std_output_files.reporting_environment,
                                                     root_file_path)
    executor = processing.SuitesExecutor(execution_reporter,
                                         DUMMY_CASE_PROCESSING,
                                         lambda conf: processor)
    exit_code = executor.execute_and_report(test_suites)
    std_output_files.finish()
    return ExitCodeAndStdOut(exit_code, std_output_files.stdout_contents)


def expected_output_from(root: ET.Element) -> str:
    tree = ET.ElementTree(root)
    stream = io.StringIO()
    tree.write(stream,
               encoding='unicode',
               xml_declaration=True,
               short_empty_elements=True)
    return stream.getvalue() + os.linesep


def _suites_xml(test_suite_elements: List[ET.Element]) -> ET.Element:
    ret_val = ET.Element('testsuites')
    ret_val.extend(test_suite_elements)
    return ret_val


def suite_xml(attributes: Dict[str, str], test_case_elements: List[ET.Element]) -> ET.Element:
    attributes.update({
        'time': TIME_VALUE_REPLACEMENT,
        'timestamp': TIMESTAMP_VALUE_REPLACEMENT,
        'hostname': platform.node(),
    })
    ret_val = ET.Element('testsuite', attributes)
    ret_val.append(ET.Element('properties'))
    ret_val.extend(test_case_elements)
    ret_val.append(ET.Element('system-out'))
    ret_val.append(ET.Element('system-err'))
    return ret_val


def successful_test_case_xml(name: str) -> ET.Element:
    return ET.Element('testcase', {
        'name': name,
        'classname': name,
        'time': TIME_VALUE_REPLACEMENT,
    })


def failing_test_case_xml(name: str,
                          failure_type: str,
                          failure_message: str) -> ET.Element:
    ret_val = ET.Element('testcase', {
        'name': name,
        'classname': name,
        'time': TIME_VALUE_REPLACEMENT,
    })
    failure = ET.SubElement(ret_val, 'failure', {
        'type': failure_type,
    })
    failure.text = failure_message
    return ret_val


def erroneous_test_case_xml(name: str,
                            error_type: str,
                            failure_message: str) -> ET.Element:
    ret_val = ET.Element('testcase', {
        'name': name,
        'classname': name,
        'time': TIME_VALUE_REPLACEMENT,
    })
    failure = ET.SubElement(ret_val, 'error', {
        'type': error_type,
    })
    failure.text = failure_message
    return ret_val


def replace_xml_variables(xml: str) -> str:
    ret_val = xml
    ret_val = _TIME_ATTRIBUTE_RE.sub(_TIME_ATTRIBUTE_REPLACEMENT, ret_val)
    ret_val = _TIMESTAMP_ATTRIBUTE_RE.sub(_TIMESTAMP_ATTRIBUTE_REPLACEMENT, ret_val)
    return ret_val


_TIME_ATTRIBUTE_RE = re.compile(r'time="[0-9]*(\.[0-9]+)?"')
TIME_VALUE_REPLACEMENT = '__TIME__'
_TIME_ATTRIBUTE_REPLACEMENT = 'time="' + TIME_VALUE_REPLACEMENT + '"'

_TIMESTAMP_ATTRIBUTE_RE = re.compile(r'timestamp="[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"')
TIMESTAMP_VALUE_REPLACEMENT = '__TIMESTAMP__'
_TIMESTAMP_ATTRIBUTE_REPLACEMENT = 'timestamp="' + TIMESTAMP_VALUE_REPLACEMENT + '"'

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
