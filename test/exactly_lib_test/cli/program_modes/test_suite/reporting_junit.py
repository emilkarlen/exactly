import pathlib
import unittest

from exactly_lib.util.string import lines_content
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    run_via_main_program_internally_with_default_setup
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_resources.main_program import main_program_check_for_test_suite
from exactly_lib_test.test_resources.main_program.main_program_check_base import \
    tests_for_setup_without_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_suite.reporters.junit import suite_xml, successful_test_case_xml, expected_output_from


class SuiteWithSingleEmptyTestCase(main_program_check_for_test_suite.SetupWithoutPreprocessorWithTestActor):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]', 'the.case'])),
            File('the.case', ''),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return []

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_xml = suite_xml(attributes={
            'name': 'main.suite',
            'tests': '1'},
            test_case_elements=[successful_test_case_xml('the.case')]
        )
        expected_output = expected_output_from(expected_xml)
        return [expected_output]

    def expected_exit_code(self) -> int:
        return 0


_TESTS = [
    SuiteWithSingleEmptyTestCase(),
]


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(
        tests_for_setup_without_preprocessor(_TESTS,
                                             main_program_runner))
    return ret_val


def suite_for_running_main_program_internally() -> unittest.TestSuite:
    return suite_for(run_via_main_program_internally_with_default_setup())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite_for_running_main_program_internally())
