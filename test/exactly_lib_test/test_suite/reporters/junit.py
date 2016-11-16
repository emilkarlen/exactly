import io
import os
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

from exactly_lib.execution import result
from exactly_lib.processing import test_case_processing
from exactly_lib.test_suite import execution
from exactly_lib.test_suite.execution import SuitesExecutor
from exactly_lib.test_suite.reporters import junit as sut
from exactly_lib_test.test_resources.str_std_out_files import StringStdOutFiles
from exactly_lib_test.test_suite.test_resources.execution_utils import FULL_RESULT_PASS, test_suite
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


def suite_executor_for_case_processing_that_unconditionally(execution_result: result.FullResult,
                                                            std_output_files: StringStdOutFiles,
                                                            root_file_path: Path) -> SuitesExecutor:
    factory = sut.JUnitRootSuiteReporterFactory()
    root_suite_reporter = factory.new_reporter(std_output_files.stdout_files, root_file_path)
    case_result = test_case_processing.new_executed(execution_result)
    return execution.SuitesExecutor(root_suite_reporter, DUMMY_CASE_PROCESSING,
                                    lambda conf: TestCaseProcessorThatGivesConstant(case_result))


def execute_with_case_processing_with_constant_result(test_case_execution_result: result.FullResult,
                                                      root_file_path: Path,
                                                      test_suites: list) -> ExitCodeAndStdOut:
    std_output_files = StringStdOutFiles()
    factory = sut.JUnitRootSuiteReporterFactory()
    root_suite_reporter = factory.new_reporter(std_output_files.stdout_files, root_file_path)
    case_result = test_case_processing.new_executed(test_case_execution_result)
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
