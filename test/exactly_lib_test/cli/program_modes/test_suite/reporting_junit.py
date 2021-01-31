import pathlib
import unittest
from typing import List

import exactly_lib.cli.definitions.common_cli_options as opt
from exactly_lib.cli.definitions.program_modes.test_suite import command_line_options
from exactly_lib.definitions.entity import suite_reporters
from exactly_lib.util.cli_syntax import short_and_long_option_syntax
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.main_program import main_program_check_for_test_suite, main_program_check_base
from exactly_lib_test.test_resources.main_program.main_program_check_base import \
    tests_for_setup_without_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions import xml_etree as asrt_xml
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.test_suite.reporters.junit import suite_xml, successful_test_case_xml, replace_xml_variables


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(
        tests_for_setup_without_preprocessor(_TESTS,
                                             main_program_runner))
    return ret_val


class SuiteWithSingleEmptyTestCase(main_program_check_base.SetupWithoutPreprocessor,
                                   main_program_check_for_test_suite.SetupBase):
    def file_argument_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return self.root_suite_file_based_at(root_path)

    def arguments_for_interpreter(self) -> List[str]:
        return main_program_check_for_test_suite.ARGUMENTS_FOR_TEST_INTERPRETER

    def first_arguments(self, root_path: pathlib.Path) -> List[str]:
        return [opt.SUITE_COMMAND,
                short_and_long_option_syntax.long_syntax(command_line_options.OPTION_FOR_REPORTER__LONG),
                suite_reporters.JUNIT_REPORTER.singular_name]

    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]', 'the.case'])),
            File('the.case', ''),
        ])

    def stdout_expectation(self, root_path: pathlib.Path) -> Assertion[str]:
        expected_xml = suite_xml(
            attributes={
                'name': 'main.suite',
                'tests': '1',
                'errors': '0',
                'failures': '0',
            },
            test_case_elements=[successful_test_case_xml('the.case')]
        )
        return asrt_xml.str_as_xml_equals(expected_xml)

    def expected_exit_code(self) -> int:
        return 0

    def check(self,
              put: unittest.TestCase,
              root_path: pathlib.Path,
              actual_result: SubProcessResult):
        self._check_base(put, root_path, actual_result)

    def _translate_actual_stdout_before_assertion(self, output_on_stdout: str) -> str:
        return replace_xml_variables(output_on_stdout)


_TESTS = [
    SuiteWithSingleEmptyTestCase(),
]
