import pathlib

from shellcheck_lib.default.program_modes.test_suite.reporting import FAILED_TESTS_EXIT_CODE
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.test_case.test_case_processing import AccessErrorType
from shellcheck_lib.util.string import lines_content
from shellcheck_lib_test.test_resources import quoting
from shellcheck_lib_test.test_resources.file_structure import DirContents, File
from shellcheck_lib_test.test_resources.main_program import main_program_check_for_test_suite


class PreprocessorIsAppliedWithTestCaseFileAsArgument(main_program_check_for_test_suite.SetupWithPreprocessor):
    if_basename_is_pass_then_empty_tc_else_tc_that_will_cause_parser_error = """
import sys
import os.path

basename = os.path.basename(sys.argv[1])
if basename == 'pass':
    print('# valid empty test case that PASS')
else:
    print('invalid test case that will cause PARSER-ERROR')
"""

    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def preprocessor_source(self) -> str:
        return self.if_basename_is_pass_then_empty_tc_else_tc_that_will_cause_parser_error

    def file_structure(self, root_path: pathlib.Path,
                       python_executable_file_name: str,
                       preprocessor_source_file_name: str) -> DirContents:
        preprocessor = '%s %s' % (quoting.file_name(python_executable_file_name),
                                  quoting.file_name(preprocessor_source_file_name))
        return DirContents([
            File('main.suite',
                 lines_content(['preprocessor ' + preprocessor
                                   ,
                                '[cases]',
                                'pass',
                                'parser-error'])),
            File('pass', 'original content that would PARSE-ERROR, if it was not preprocessed'),
            File('parser-error', '# empty content that would PASS, if it was not preprocessed'),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / 'main.suite'),
            self.case(root_path / 'pass', FullResultStatus.PASS.name),
            self.case(root_path / 'parser-error', AccessErrorType.PARSE_ERROR.name),
            self.suite_end(root_path / 'main.suite'),
        ]

    def expected_exit_code(self) -> int:
        return FAILED_TESTS_EXIT_CODE
