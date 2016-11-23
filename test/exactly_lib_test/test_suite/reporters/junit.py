import io
import os
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

from exactly_lib.execution.result_reporting import error_message_for_full_result, error_message_for_error_info
from exactly_lib.processing import test_case_processing as tcp
from exactly_lib.processing.test_case_processing import Result, AccessErrorType
from exactly_lib.test_suite import execution
from exactly_lib.test_suite import structure
from exactly_lib.test_suite.reporters import junit as sut
from exactly_lib_test.test_case.test_resources import error_info
from exactly_lib_test.test_resources.str_std_out_files import StringStdOutFiles
from exactly_lib_test.test_suite.reporters.test_resources import FULL_RESULT_HARD_ERROR, FULL_RESULT_VALIDATE, \
    FULL_RESULT_IMPLEMENTATION_ERROR, FULL_RESULT_XPASS, FULL_RESULT_XFAIL
from exactly_lib_test.test_suite.test_resources.execution_utils import FULL_RESULT_PASS, test_suite, test_case, \
    FULL_RESULT_FAIL, FULL_RESULT_SKIP, TestCaseProcessorThatGivesConstantPerCase
from exactly_lib_test.test_suite.test_resources.execution_utils import TestCaseProcessorThatGivesConstant, \
    DUMMY_CASE_PROCESSING


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestExecutionOfSingleSuiteWithSingleTestCase),
        unittest.makeSuite(TestExecutionOfSingleSuiteWithMultipleTestCases),
        unittest.makeSuite(TestExecutionOfSuiteWithoutTestCasesButWithSubSuites),
        unittest.makeSuite(TestExecutionOfRootSuiteWithBothTestCasesAndSubSuites),
    ])


class TestExecutionOfSingleSuiteWithSingleTestCase(unittest.TestCase):
    def test_empty_suite(self):
        # ARRANGE #
        expected_xml = ET.Element('testsuite', {
            'name': 'root file name',
            'tests': '0'
        })
        expected_output = expected_output_from(expected_xml)
        root_suite = test_suite('root file name', [], [])
        test_suites = [root_suite]
        # ACT #
        actual = execute_with_case_processing_with_constant_result(FULL_RESULT_PASS,
                                                                   root_suite,
                                                                   Path(),
                                                                   test_suites)
        # ASSERT #
        self.assertEquals(0, actual.exit_code)
        self.assertEqual(expected_output, actual.stdout)

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
                    'tests': '1'},
                    test_case_elements=[successful_test_case_xml('test case file name')]
                )
                expected_output = expected_output_from(expected_xml)
                root_suite = test_suite('suite that passes', [], [test_case('test case file name')])
                test_suites = [root_suite]
                # ACT #
                actual = execute_with_case_processing_with_constant_result(
                    tcp.new_executed(case_result),
                    root_suite,
                    Path(),
                    test_suites)

                # ASSERT #
                self.assertEquals(0, actual.exit_code)
                self.assertEqual(expected_output, actual.stdout)

    def test_single_case_with_error(self):
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
                    erroneous_test_case_xml('test case file name',
                                            failure_message=error_message_for_full_result(case_result)))
                expected_output = expected_output_from(expected_xml)
                root_suite = test_suite('suite with error', [], [test_case('test case file name')])
                test_suites = [root_suite]
                # ACT #
                actual = execute_with_case_processing_with_constant_result(
                    tcp.new_executed(case_result),
                    root_suite,
                    Path(),
                    test_suites)

                # ASSERT #
                self.assertEquals(0, actual.exit_code)
                self.assertEqual(expected_output, actual.stdout)

    def test_single_case_with_error_due_to_failure_to_execute(self):
        cases = [
            tcp.new_internal_error(error_info.of_message('error message')),
            tcp.new_access_error(AccessErrorType.FILE_ACCESS_ERROR,
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
                    erroneous_test_case_xml('test case file name',
                                            failure_message=error_message_for_error_info(case_result.error_info)))
                expected_output = expected_output_from(expected_xml)
                root_suite = test_suite('suite with error', [], [test_case('test case file name')])
                test_suites = [root_suite]
                # ACT #
                actual = execute_with_case_processing_with_constant_result(
                    case_result,
                    root_suite,
                    Path(),
                    test_suites)

                # ASSERT #
                self.assertEquals(0, actual.exit_code)
                self.assertEqual(expected_output, actual.stdout)

    def test_single_case_with_failure(self):
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
                    failing_test_case_xml('test case file name',
                                          failure_message=error_message_for_full_result(case_result)))
                expected_output = expected_output_from(expected_xml)
                root_suite = test_suite('suite with failure', [], [test_case('test case file name')])
                test_suites = [root_suite]
                # ACT #
                actual = execute_with_case_processing_with_constant_result(
                    tcp.new_executed(case_result),
                    root_suite,
                    Path(),
                    test_suites)
                # ASSERT #
                self.assertEquals(0, actual.exit_code)
                self.assertEqual(expected_output, actual.stdout)


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
            'failures': '1',
            'errors': '1'},
            test_case_elements=[
                successful_test_case_xml('successful case'),
                failing_test_case_xml('failing case', error_message_for_full_result(FULL_RESULT_FAIL)),
                erroneous_test_case_xml('erroneous case', error_message_for_full_result(FULL_RESULT_HARD_ERROR)),
            ]
        )
        expected_output = expected_output_from(expected_xml)
        self.assertEquals(0, actual.exit_code)
        self.assertEqual(expected_output, actual.stdout)


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
                'package': 'root suite file name',
                'id': '1',
                'tests': '1'},
                test_case_elements=[successful_test_case_xml('the test case')]
            ),
        ])
        expected_output = expected_output_from(expected_xml)
        self.assertEquals(0, actual.exit_code)
        self.assertEqual(expected_output, actual.stdout)

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
                'package': 'root suite file name',
                'id': '1',
                'tests': '1'},
                test_case_elements=[successful_test_case_xml('successful case')]
            ),
            suite_xml(attributes={
                'name': 'suite with failing and erroneous case',
                'package': 'root suite file name',
                'id': '2',
                'tests': '2',
                'failures': '1',
                'errors': '1'},
                test_case_elements=[
                    failing_test_case_xml('failing case', error_message_for_full_result(FULL_RESULT_FAIL)),
                    erroneous_test_case_xml('erroneous case', error_message_for_full_result(FULL_RESULT_HARD_ERROR)),
                ]
            ),
        ])
        expected_output = expected_output_from(expected_xml)
        self.assertEquals(0, actual.exit_code)
        self.assertEqual(expected_output, actual.stdout)


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
                'package': 'root suite file name',
                'id': '1',
                'tests': '1'},
                test_case_elements=[successful_test_case_xml('test case in root suite')]
            ),
            suite_xml(attributes={
                'name': 'suite with single case',
                'package': 'root suite file name',
                'id': '2',
                'tests': '1'},
                test_case_elements=[successful_test_case_xml('test case in sub suite')]
            ),
        ])
        expected_output = expected_output_from(expected_xml)
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


def execute_with_case_processing_with_constant_result(case_result: Result,
                                                      root_suite: structure.TestSuite,
                                                      root_file_path: Path,
                                                      test_suites: list) -> ExitCodeAndStdOut:
    return execute_with_case_processing_with_constant_processor(TestCaseProcessorThatGivesConstant(case_result),
                                                                root_suite,
                                                                root_file_path,
                                                                test_suites)


def execute_with_case_processing_with_constant_processor(processor: tcp.Processor,
                                                         root_suite: structure.TestSuite,
                                                         root_file_path: Path,
                                                         test_suites: list) -> ExitCodeAndStdOut:
    std_output_files = StringStdOutFiles()
    factory = sut.JUnitRootSuiteReporterFactory()
    root_suite_reporter = factory.new_reporter(root_suite, std_output_files.stdout_files, root_file_path)
    executor = execution.SuitesExecutor(root_suite_reporter,
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


def _suites_xml(test_suite_elements: list) -> ET.Element:
    ret_val = ET.Element('testsuites')
    ret_val.extend(test_suite_elements)
    return ret_val


def suite_xml(attributes: dict, test_case_elements: list) -> ET.Element:
    ret_val = ET.Element('testsuite', attributes)
    ret_val.extend(test_case_elements)
    return ret_val


def successful_test_case_xml(name: str) -> ET.Element:
    return ET.Element('testcase', {
        'name': name,
    })


def failing_test_case_xml(name: str, failure_message: str) -> ET.Element:
    ret_val = ET.Element('testcase', {
        'name': name,
    })
    failure = ET.SubElement(ret_val, 'failure')
    failure.text = failure_message
    return ret_val


def erroneous_test_case_xml(name: str, failure_message: str) -> ET.Element:
    ret_val = ET.Element('testcase', {
        'name': name,
    })
    failure = ET.SubElement(ret_val, 'error')
    failure.text = failure_message
    return ret_val
