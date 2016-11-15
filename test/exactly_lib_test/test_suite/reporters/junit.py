import io
import os
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

from exactly_lib.test_suite import exit_values as suite_ev
from exactly_lib_test.test_resources.str_std_out_files import StringStdOutFiles
from exactly_lib_test.test_suite.reporters.test_resources import suite_executor_for_case_processing_that_unconditionally
from exactly_lib_test.test_suite.test_resources.execution_utils import FULL_RESULT_PASS, test_suite


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestExecutionOfSuite),
    ])


class TestExecutionOfSuite(unittest.TestCase):
    def test_single_empty_suite(self):
        # ARRANGE #
        expected_exit_value = suite_ev.ALL_PASS
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
        exit_value = executor.execute_and_report(test_suites)
        # ASSERT #
        std_output_files.finish()

        self.assertEquals(expected_exit_value, exit_value)
        self.assertEqual(expected_output, std_output_files.stdout_contents)


def expected_output_from(root: ET.Element) -> str:
    tree = ET.ElementTree(root)
    stream = io.StringIO()
    tree.write(stream, encoding='unicode',
               xml_declaration=True,
               short_empty_elements=True)
    return stream.getvalue() + os.linesep
