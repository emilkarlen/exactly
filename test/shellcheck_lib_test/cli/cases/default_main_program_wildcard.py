import pathlib

from shellcheck_lib.default.execution_mode.test_suite.reporting import INVALID_SUITE_EXIT_CODE

from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib_test.util import check_suite
from shellcheck_lib_test.util.file_structure import DirContents, Dir, File
from shellcheck_lib_test.util.with_tmp_file import lines_content


class SuiteWithWildcardReferencesToCaseFilesThatMatchesNoFilesTypeQuestionMark(check_suite.Setup):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              '?.case'])),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / 'main.suite'),
            self.suite_end(root_path / 'main.suite'),
        ]

    def expected_exit_code(self) -> int:
        return 0


class SuiteWithWildcardReferencesToCaseFilesThatMatchesFilesTypeQuestionMark(check_suite.Setup):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              '?.case'])),
            File('b.case', ''),
            File('a.case', ''),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / 'main.suite'),
            self.case(root_path / 'a.case', FullResultStatus.PASS.name),
            self.case(root_path / 'b.case', FullResultStatus.PASS.name),
            self.suite_end(root_path / 'main.suite'),
        ]

    def expected_exit_code(self) -> int:
        return 0


class SuiteWithWildcardReferencesToCaseFilesThatAreDirectories(check_suite.Setup):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              '?'])),
            File('1', ''),
            Dir('2', []),
            File('3', ''),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return []

    def expected_exit_code(self) -> int:
        return INVALID_SUITE_EXIT_CODE


class SuiteWithWildcardReferencesToCaseFilesInSubDirThatMatchesFiles(check_suite.Setup):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              'sub-dir-1/?.case',
                                              'sub-dir-2/*.case'])),
            Dir('sub-dir-1', [
                File('b.case', ''),
                File('a.case', ''),
            ]),
            Dir('sub-dir-2', [
                File('22.case', ''),
                File('11.case', ''),
            ]),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / 'main.suite'),
            self.case(root_path / 'sub-dir-1' / 'a.case', FullResultStatus.PASS.name),
            self.case(root_path / 'sub-dir-1' / 'b.case', FullResultStatus.PASS.name),
            self.case(root_path / 'sub-dir-2' / '11.case', FullResultStatus.PASS.name),
            self.case(root_path / 'sub-dir-2' / '22.case', FullResultStatus.PASS.name),
            self.suite_end(root_path / 'main.suite'),
        ]

    def expected_exit_code(self) -> int:
        return 0
