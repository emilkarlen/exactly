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
            empty_file('b.case'),
            empty_file('a.case'),
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


class SuiteWithWildcardReferencesToCaseFilesInAnyDirectSubDir(check_suite.Setup):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              '*/*.case'])),
            Dir('sub-dir-2', [
                empty_file('y.case'),
                empty_file('x.case'),
            ]),
            Dir('sub-dir-1', [
                empty_file('b.case'),
                empty_file('a.case'),
                Dir('sub-dir-1-1', [
                    empty_file('1-1.case'),
                ])
            ]),
            empty_file('1.case'),
            empty_file('2.case'),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / 'main.suite'),
            self.case(root_path / 'sub-dir-1' / 'a.case', FullResultStatus.PASS.name),
            self.case(root_path / 'sub-dir-1' / 'b.case', FullResultStatus.PASS.name),
            self.case(root_path / 'sub-dir-2' / 'x.case', FullResultStatus.PASS.name),
            self.case(root_path / 'sub-dir-2' / 'y.case', FullResultStatus.PASS.name),
            self.suite_end(root_path / 'main.suite'),
        ]

    def expected_exit_code(self) -> int:
        return 0


class SuiteWithWildcardReferencesToCaseFilesInAnySubDir(check_suite.Setup):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              '**/*.case'])),
            Dir('sub-dir-2', [
                empty_file('y.case'),
                empty_file('x.case'),
            ]),
            Dir('sub-dir-1', [
                empty_file('b.case'),
                empty_file('a.case'),
                Dir('sub-dir-1-1', [
                    empty_file('1-1.case'),
                ])
            ]),
            empty_file('1.case'),
            empty_file('2.case'),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / 'main.suite'),
            self.case(root_path / '1.case', FullResultStatus.PASS.name),
            self.case(root_path / '2.case', FullResultStatus.PASS.name),
            self.case(root_path / 'sub-dir-1' / 'a.case', FullResultStatus.PASS.name),
            self.case(root_path / 'sub-dir-1' / 'b.case', FullResultStatus.PASS.name),
            self.case(root_path / 'sub-dir-1' / 'sub-dir-1-1' / '1-1.case', FullResultStatus.PASS.name),
            self.case(root_path / 'sub-dir-2' / 'x.case', FullResultStatus.PASS.name),
            self.case(root_path / 'sub-dir-2' / 'y.case', FullResultStatus.PASS.name),
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
            empty_file('1'),
            Dir('2', []),
            empty_file('3'),
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
                empty_file('b.case'),
                empty_file('a.case'),
            ]),
            Dir('sub-dir-2', [
                empty_file('22.case'),
                empty_file('11.case'),
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


def empty_file(file_name: str) -> File:
    return File(file_name, '')
