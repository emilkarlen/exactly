import pathlib

from shellcheck_lib.default.execution_mode.test_suite.reporting import FAILED_TESTS_EXIT_CODE
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib_test.util.check_suite import SetupWithPreprocessor
from shellcheck_lib_test.util.file_structure import DirContents, File, empty_file
from shellcheck_lib_test.util.with_tmp_file import lines_content


class PreprocessorIsAppliedWithTestCaseFileAsArgument(SetupWithPreprocessor):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        root_path / 'main.suite'

    def preprocessor_source(self) -> str:
        return """
        import sys
        import os.path

        basename = os.path.basename(sys.argv[1])
        if basename == 'pass':
            print('# valid empty test case that passes')
        else:
            print('invalid test case')
        """

    def file_structure(self, root_path: pathlib.Path,
                       python_executable_file_name: str,
                       preprocessor_source_file_name: str) -> DirContents:
        return DirContents([
            File('main.suite',
                 lines_content(['preprocessor ' + python_executable_file_name + ' ' + preprocessor_source_file_name,
                                '[cases]',
                                'pass',
                                'invalid'])),
            empty_file('pass'),
            empty_file('invalid'),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / 'main.suite'),
            self.case(root_path / 'pass', FullResultStatus.PASS.name),
            self.case(root_path / 'pass', FullResultStatus.HARD_ERROR.name),
            self.suite_end(root_path / 'main.suite'),
        ]

    def expected_exit_code(self) -> int:
        return FAILED_TESTS_EXIT_CODE
