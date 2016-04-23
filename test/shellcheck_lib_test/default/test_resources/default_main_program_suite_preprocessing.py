import pathlib

from shellcheck_lib.cli.cli_environment.program_modes.test_case.exit_values import EXECUTION__PASS, \
    NO_EXECUTION__PARSE_ERROR
from shellcheck_lib.cli.cli_environment.program_modes.test_suite import exit_values
from shellcheck_lib.document.syntax import section_header
from shellcheck_lib.execution import phases
from shellcheck_lib.util.string import lines_content
from shellcheck_lib_test.test_resources import quoting
from shellcheck_lib_test.test_resources.file_structure import DirContents, File
from shellcheck_lib_test.test_resources.main_program import main_program_check_for_test_suite
from shellcheck_lib_test.test_resources.program_modes.suite import reporting_output


class PreprocessorIsAppliedWithTestCaseFileAsArgument(main_program_check_for_test_suite.SetupWithPreprocessor):
    if_basename_is_pass_then_empty_tc_else_tc_that_will_cause_parser_error = """
import sys
import os.path
import os

basename = os.path.basename(sys.argv[1])
if basename == 'pass':
    print('{section_header_for_phase_with_instructions}' + os.linesep + '# valid empty test case that PASS')
else:
    print('{section_header_for_phase_with_instructions}' + os.linesep + 'invalid test case that will cause PARSER-ERROR')
""".format(section_header_for_phase_with_instructions=section_header(phases.SETUP.section_name))

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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return [
            reporting_output.suite_begin(root_path / 'main.suite'),
            reporting_output.case(root_path / 'pass', EXECUTION__PASS.exit_identifier),
            reporting_output.case(root_path / 'parser-error', NO_EXECUTION__PARSE_ERROR.exit_identifier),
            reporting_output.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary_for_valid_suite(root_path, 2, exit_values.FAILED_TESTS)

    def expected_exit_code(self) -> int:
        return exit_values.FAILED_TESTS.exit_code
