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
        std_output_files = StringStdOutFiles()
        executor = suite_executor_for_case_processing_that_unconditionally(FULL_RESULT_PASS,
                                                                           std_output_files,
                                                                           Path())
        # ACT #
        exit_code = executor.execute_and_report(test_suites)
        # ASSERT #
        std_output_files.finish()

        self.assertEquals(0, exit_code)
        self.assertEqual(expected_output, std_output_files.stdout_contents)


def suite_executor_for_case_processing_that_unconditionally(execution_result: result.FullResult,
                                                            std_output_files: StringStdOutFiles,
                                                            root_file_path: Path) -> SuitesExecutor:
    factory = sut.JUnitRootSuiteReporterFactory()
    root_suite_reporter = factory.new_reporter(std_output_files.stdout_files, root_file_path)
    case_result = test_case_processing.new_executed(execution_result)
    return execution.SuitesExecutor(root_suite_reporter, DUMMY_CASE_PROCESSING,
                                    lambda conf: TestCaseProcessorThatGivesConstant(case_result))


def expected_output_from(root: ET.Element) -> str:
    tree = ET.ElementTree(root)
    stream = io.StringIO()
    tree.write(stream,
               encoding='unicode',
               xml_declaration=True,
               short_empty_elements=True)
    return stream.getvalue() + os.linesep
