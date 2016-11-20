import io
import os
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

from exactly_lib.execution.result_reporting import error_message_for_full_result, error_message_for_error_info
from exactly_lib.processing import test_case_processing
from exactly_lib.processing.test_case_processing import Result, AccessErrorType
from exactly_lib.test_suite import execution
from exactly_lib.test_suite.execution import SuitesExecutor
from exactly_lib.test_suite.reporters import junit as sut
from exactly_lib_test.test_case.test_resources import error_info
from exactly_lib_test.test_resources.str_std_out_files import StringStdOutFiles
from exactly_lib_test.test_suite.reporters.test_resources import FULL_RESULT_HARD_ERROR, FULL_RESULT_VALIDATE, \
    FULL_RESULT_IMPLEMENTATION_ERROR, FULL_RESULT_XPASS, FULL_RESULT_XFAIL
from exactly_lib_test.test_suite.test_resources.execution_utils import FULL_RESULT_PASS, test_suite, test_case, \
    FULL_RESULT_FAIL, FULL_RESULT_SKIP
from exactly_lib_test.test_suite.test_resources.execution_utils import TestCaseProcessorThatGivesConstant, \
    DUMMY_CASE_PROCESSING


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestExecutionOfSuite),
    ])


class TestExecutionOfSuite(unittest.TestCase):
    def test_single_empty_suite(self):
        # ARRANGE #
        expected_xml = ET.Element('testsuite', {
            'name': 'root file name',
            'tests': '0'
        })
        expected_output = expected_output_from(expected_xml)
        test_suites = [
            test_suite('root file name', [], [])
        ]
        # ACT #
        actual = execute_with_case_processing_with_constant_result(FULL_RESULT_PASS,
                                                                   Path(),
                                                                   test_suites)
        # ASSERT #
        self.assertEquals(0, actual.exit_code)
        self.assertEqual(expected_output, actual.stdout)

    def test_suite_with_single_case_that_passes(self):
        cases = [
            FULL_RESULT_PASS,
            FULL_RESULT_XFAIL,
            FULL_RESULT_SKIP,
        ]
        for case_result in cases:
            with self.subTest(case_result_status=case_result.status):
                # ARRANGE #
                expected_xml = ET.Element('testsuite', {
                    'name': 'suite that passes',
                    'tests': '1',
                })
                expected_xml.append(
                    _successful_test_case('test case file name'))
                expected_output = expected_output_from(expected_xml)
                test_suites = [
                    test_suite('suite that passes', [], [
                        test_case('test case file name')
                    ])
                ]
                # ACT #
                actual = execute_with_case_processing_with_constant_result(
                    test_case_processing.new_executed(case_result),
                    Path(),
                    test_suites)

                # ASSERT #
                self.assertEquals(0, actual.exit_code)
                self.assertEqual(expected_output, actual.stdout)

    def test_suite_with_single_case_with_error(self):
        cases = [
            FULL_RESULT_HARD_ERROR,
            FULL_RESULT_VALIDATE,
            FULL_RESULT_IMPLEMENTATION_ERROR,
        ]
        for case_result in cases:
            with self.subTest(case_result_status=case_result.status):
                # ARRANGE #
                expected_xml = ET.Element('testsuite', {
                    'name': 'suite with error',
                    'tests': '1',
                    'errors': '1'
                })
                expected_xml.append(
                    _failing_test_case('test case file name',
                                       failure_message=error_message_for_full_result(case_result)))
                expected_output = expected_output_from(expected_xml)
                test_suites = [
                    test_suite('suite with error', [], [
                        test_case('test case file name')
                    ])
                ]
                # ACT #
                actual = execute_with_case_processing_with_constant_result(
                    test_case_processing.new_executed(case_result),
                    Path(),
                    test_suites)

                # ASSERT #
                self.assertEquals(0, actual.exit_code)
                self.assertEqual(expected_output, actual.stdout)

    def test_suite_with_single_case_with_error_due_to_failure_to_execute(self):
        cases = [
            test_case_processing.new_internal_error(error_info.of_message('error message')),
            test_case_processing.new_access_error(AccessErrorType.FILE_ACCESS_ERROR,
                                                  error_info.of_message('error message')),
        ]
        for case_result in cases:
            with self.subTest(case_result_status=case_result.status):
                # ARRANGE #
                expected_xml = ET.Element('testsuite', {
                    'name': 'suite with error',
                    'tests': '1',
                    'errors': '1'
                })
                expected_xml.append(
                    _failing_test_case('test case file name',
                                       failure_message=error_message_for_error_info(case_result.error_info)))
                expected_output = expected_output_from(expected_xml)
                test_suites = [
                    test_suite('suite with error', [], [
                        test_case('test case file name')
                    ])
                ]
                # ACT #
                actual = execute_with_case_processing_with_constant_result(
                    case_result,
                    Path(),
                    test_suites)

                # ASSERT #
                self.assertEquals(0, actual.exit_code)
                self.assertEqual(expected_output, actual.stdout)

    def test_suite_with_single_case_with_failure(self):
        cases = [
            FULL_RESULT_FAIL,
            FULL_RESULT_XPASS,
        ]
        for case_result in cases:
            with self.subTest(case_result_status=case_result.status):
                # ARRANGE #
                expected_xml = ET.Element('testsuite', {
                    'name': 'suite with failure',
                    'tests': '1',
                    'failures': '1'
                })
                expected_xml.append(
                    _failing_test_case('test case file name',
                                       failure_message=error_message_for_full_result(case_result)))
                expected_output = expected_output_from(expected_xml)
                test_suites = [
                    test_suite('suite with failure', [], [
                        test_case('test case file name')
                    ])
                ]
                # ACT #
                actual = execute_with_case_processing_with_constant_result(
                    test_case_processing.new_executed(case_result),
                    Path(),
                    test_suites)

                # ASSERT #
                self.assertEquals(0, actual.exit_code)
                self.assertEqual(expected_output, actual.stdout)


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


def suite_executor_for_case_processing_that_unconditionally(case_result: Result,
                                                            std_output_files: StringStdOutFiles,
                                                            root_file_path: Path) -> SuitesExecutor:
    factory = sut.JUnitRootSuiteReporterFactory()
    root_suite_reporter = factory.new_reporter(std_output_files.stdout_files, root_file_path)
    return execution.SuitesExecutor(root_suite_reporter, DUMMY_CASE_PROCESSING,
                                    lambda conf: TestCaseProcessorThatGivesConstant(case_result))


def execute_with_case_processing_with_constant_result(case_result: Result,
                                                      root_file_path: Path,
                                                      test_suites: list) -> ExitCodeAndStdOut:
    std_output_files = StringStdOutFiles()
    factory = sut.JUnitRootSuiteReporterFactory()
    root_suite_reporter = factory.new_reporter(std_output_files.stdout_files, root_file_path)
    executor = execution.SuitesExecutor(root_suite_reporter, DUMMY_CASE_PROCESSING,
                                        lambda conf: TestCaseProcessorThatGivesConstant(case_result))
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


def _successful_test_case(name: str) -> ET.Element:
    return ET.Element('testcase', {
        'name': name,
    })


def _failing_test_case(name: str, failure_message: str) -> ET.Element:
    ret_val = ET.Element('testcase', {
        'name': name,
    })
    failure = ET.SubElement(ret_val, 'failure')
    failure.text = failure_message
    return ret_val
