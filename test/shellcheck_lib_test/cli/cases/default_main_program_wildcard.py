import pathlib

from shellcheck_lib.default.execution_mode.test_suite.reporting import INVALID_SUITE_EXIT_CODE
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib_test.util import check_suite
from shellcheck_lib_test.util.file_structure import DirContents, Dir, File
from shellcheck_lib_test.util.with_tmp_file import lines_content


class ReferencesToCaseFilesThatMatchesNoFiles(check_suite.Setup):
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


class ReferencesToSuiteFilesThatMatchesNoFiles(check_suite.Setup):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[suites]',
                                              '?.suite'])),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / 'main.suite'),
            self.suite_end(root_path / 'main.suite'),
        ]

    def expected_exit_code(self) -> int:
        return 0


class ReferencesToCaseFilesThatMatchesFilesTypeQuestionMark(check_suite.Setup):
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


class ReferencesToCaseFilesThatMatchesFilesTypeCharacterRange(check_suite.Setup):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              '_[a-bx].case'])),
            empty_file('_b.case'),
            empty_file('_x.case'),
            empty_file('_a.case'),
            empty_file('_c.case'),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / 'main.suite'),
            self.case(root_path / '_a.case', FullResultStatus.PASS.name),
            self.case(root_path / '_b.case', FullResultStatus.PASS.name),
            self.case(root_path / '_x.case', FullResultStatus.PASS.name),
            self.suite_end(root_path / 'main.suite'),
        ]

    def expected_exit_code(self) -> int:
        return 0


class ReferencesToSuiteFilesThatMatchesFilesTypeCharacterRange(check_suite.Setup):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[suites]',
                                              '_[a-bx].suite'])),
            empty_file('_b.suite'),
            empty_file('_x.suite'),
            empty_file('_a.suite'),
            empty_file('_c.suite'),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / '_a.suite'),
            self.suite_end(root_path / '_a.suite'),
            self.suite_begin(root_path / '_b.suite'),
            self.suite_end(root_path / '_b.suite'),
            self.suite_begin(root_path / '_x.suite'),
            self.suite_end(root_path / '_x.suite'),
            self.suite_begin(root_path / 'main.suite'),
            self.suite_end(root_path / 'main.suite'),
        ]

    def expected_exit_code(self) -> int:
        return 0


class ReferencesToCaseFilesThatMatchesFilesTypeNegatedCharacterRange(check_suite.Setup):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              '_[!a-bx].case'])),
            empty_file('_b.case'),
            empty_file('_x.case'),
            empty_file('_a.case'),
            empty_file('_c.case'),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / 'main.suite'),
            self.case(root_path / '_c.case', FullResultStatus.PASS.name),
            self.suite_end(root_path / 'main.suite'),
        ]

    def expected_exit_code(self) -> int:
        return 0


class ReferencesToCaseFilesInAnyDirectSubDir(check_suite.Setup):
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


class ReferencesToSuiteFilesInAnyDirectSubDir(check_suite.Setup):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[suites]',
                                              '*/*.suite'])),
            Dir('sub-dir-2', [
                empty_file('y.suite'),
                empty_file('x.suite'),
            ]),
            Dir('sub-dir-1', [
                empty_file('b.suite'),
                empty_file('a.suite'),
                Dir('sub-dir-1-1', [
                    empty_file('1-1.suite'),
                ])
            ]),
            empty_file('1.suite'),
            empty_file('2.suite'),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / 'sub-dir-1' / 'a.suite'),
            self.suite_end(root_path / 'sub-dir-1' / 'a.suite'),
            self.suite_begin(root_path / 'sub-dir-1' / 'b.suite'),
            self.suite_end(root_path / 'sub-dir-1' / 'b.suite'),
            self.suite_begin(root_path / 'sub-dir-2' / 'x.suite'),
            self.suite_end(root_path / 'sub-dir-2' / 'x.suite'),
            self.suite_begin(root_path / 'sub-dir-2' / 'y.suite'),
            self.suite_end(root_path / 'sub-dir-2' / 'y.suite'),
            self.suite_begin(root_path / 'main.suite'),
            self.suite_end(root_path / 'main.suite'),
        ]

    def expected_exit_code(self) -> int:
        return 0


class ReferencesToCaseFilesInAnySubDir(check_suite.Setup):
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


class ReferencesToSuiteFilesInAnySubDir(check_suite.Setup):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[suites]',
                                              '**/_*.suite'])),
            Dir('sub-dir-2', [
                empty_file('_y.suite'),
                empty_file('_x.suite'),
            ]),
            Dir('sub-dir-1', [
                empty_file('_b.suite'),
                empty_file('_a.suite'),
                Dir('sub-dir-1-1', [
                    empty_file('_1-1.suite'),
                ])
            ]),
            empty_file('_1.suite'),
            empty_file('_2.suite'),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / '_1.suite'),
            self.suite_end(root_path / '_1.suite'),
            self.suite_begin(root_path / '_2.suite'),
            self.suite_end(root_path / '_2.suite'),
            self.suite_begin(root_path / 'sub-dir-1' / '_a.suite'),
            self.suite_end(root_path / 'sub-dir-1' / '_a.suite'),
            self.suite_begin(root_path / 'sub-dir-1' / '_b.suite'),
            self.suite_end(root_path / 'sub-dir-1' / '_b.suite'),
            self.suite_begin(root_path / 'sub-dir-1' / 'sub-dir-1-1' / '_1-1.suite'),
            self.suite_end(root_path / 'sub-dir-1' / 'sub-dir-1-1' / '_1-1.suite'),
            self.suite_begin(root_path / 'sub-dir-2' / '_x.suite'),
            self.suite_end(root_path / 'sub-dir-2' / '_x.suite'),
            self.suite_begin(root_path / 'sub-dir-2' / '_y.suite'),
            self.suite_end(root_path / 'sub-dir-2' / '_y.suite'),
            self.suite_begin(root_path / 'main.suite'),
            self.suite_end(root_path / 'main.suite'),
        ]

    def expected_exit_code(self) -> int:
        return 0


class ReferencesToCaseFilesThatAreDirectories(check_suite.Setup):
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


class ReferencesToSuiteFilesThatAreDirectories(check_suite.Setup):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[suites]',
                                              '?'])),
            empty_file('1'),
            Dir('2', []),
            empty_file('3'),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return []

    def expected_exit_code(self) -> int:
        return INVALID_SUITE_EXIT_CODE


class ReferencesToCaseFilesInSubDirThatMatchesFiles(check_suite.Setup):
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
