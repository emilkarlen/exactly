import pathlib

from exactly_lib.processing.exit_values import EXECUTION__PASS, \
    NO_EXECUTION__SYNTAX_ERROR
from exactly_lib.section_document.syntax import section_header
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_suite import exit_values
from exactly_lib.util.string import lines_content
from exactly_lib_test.test_resources import quoting
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_resources.main_program import main_program_check_for_test_suite
from exactly_lib_test.test_suite.reporters.test_resources import simple_progress_reporter_output


class PreprocessorIsAppliedWithTestCaseFileAsArgument(main_program_check_for_test_suite.SetupWithPreprocessor):
    if_basename_is_pass_then_empty_tc_else_tc_that_will_cause_parser_error = """
import sys
import os.path
import os

basename = os.path.basename(sys.argv[1])
if basename == 'pass':
    print('{section_header_for_phase_with_instructions}' + os.linesep +
          '# valid empty test case that PASS')
else:
    print('{section_header_for_phase_with_instructions}' + os.linesep +
          'invalid test case that will cause PARSER-ERROR')
""".format(section_header_for_phase_with_instructions=section_header(phase_identifier.SETUP.section_name))

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
                 lines_content(['[conf]',
                                'preprocessor = ' + preprocessor,
                                '[cases]',
                                'pass',
                                'syntax-error'])),
            File('pass', 'original content that would PARSE-ERROR, if it was not preprocessed'),
            File('syntax-error', '# empty content that would PASS, if it was not preprocessed'),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.case(root_path / 'pass', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'syntax-error', NO_EXECUTION__SYNTAX_ERROR.exit_identifier),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.FAILED_TESTS)

    def expected_exit_code(self) -> int:
        return exit_values.FAILED_TESTS.exit_code

    def _translate_actual_stdout_before_assertion(self, output_on_stdout: str) -> str:
        return simple_progress_reporter_output.replace_variable_output_with_placeholders(output_on_stdout)
