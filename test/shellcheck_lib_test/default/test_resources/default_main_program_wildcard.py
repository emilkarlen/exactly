import pathlib

from shellcheck_lib.default.program_modes.test_suite.reporting import INVALID_SUITE_EXIT_CODE
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.util.string import lines_content
from shellcheck_lib_test.test_resources.file_structure import DirContents, Dir, File, empty_file
from shellcheck_lib_test.test_resources.main_program import main_program_check_for_test_suite
from shellcheck_lib_test.test_resources.program_modes.suite import reporting_output


class ReferencesToCaseFilesThatMatchesNoFiles(main_program_check_for_test_suite.SetupWithoutPreprocessor):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              '?.case'])),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return [
            reporting_output.suite_begin(root_path / 'main.suite'),
            reporting_output.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return 0


class ReferencesToSuiteFilesThatMatchesNoFiles(main_program_check_for_test_suite.SetupWithoutPreprocessor):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[suites]',
                                              '?.suite'])),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return [
            reporting_output.suite_begin(root_path / 'main.suite'),
            reporting_output.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return 0


class ReferencesToCaseFilesThatMatchesFilesTypeQuestionMark(main_program_check_for_test_suite.SetupWithoutPreprocessor):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              '?.case'])),
            empty_file('b.case'),
            empty_file('a.case'),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return [
            reporting_output.suite_begin(root_path / 'main.suite'),
            reporting_output.case(root_path / 'a.case', FullResultStatus.PASS.name),
            reporting_output.case(root_path / 'b.case', FullResultStatus.PASS.name),
            reporting_output.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return 0


class ReferencesToSuiteFilesThatMatchesFilesTypeQuestionMark(
    main_program_check_for_test_suite.SetupWithoutPreprocessor):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[suites]',
                                              '?.suite'])),
            empty_file('b.suite'),
            empty_file('a.suite'),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return [
            reporting_output.suite_begin(root_path / 'a.suite'),
            reporting_output.suite_end(root_path / 'a.suite'),
            reporting_output.suite_begin(root_path / 'b.suite'),
            reporting_output.suite_end(root_path / 'b.suite'),
            reporting_output.suite_begin(root_path / 'main.suite'),
            reporting_output.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return 0


class ReferencesToCaseFilesThatMatchesFilesTypeCharacterRange(
    main_program_check_for_test_suite.SetupWithoutPreprocessor):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return [
            reporting_output.suite_begin(root_path / 'main.suite'),
            reporting_output.case(root_path / '_a.case', FullResultStatus.PASS.name),
            reporting_output.case(root_path / '_b.case', FullResultStatus.PASS.name),
            reporting_output.case(root_path / '_x.case', FullResultStatus.PASS.name),
            reporting_output.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return 0


class ReferencesToSuiteFilesThatMatchesFilesTypeCharacterRange(
    main_program_check_for_test_suite.SetupWithoutPreprocessor):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return [
            reporting_output.suite_begin(root_path / '_a.suite'),
            reporting_output.suite_end(root_path / '_a.suite'),
            reporting_output.suite_begin(root_path / '_b.suite'),
            reporting_output.suite_end(root_path / '_b.suite'),
            reporting_output.suite_begin(root_path / '_x.suite'),
            reporting_output.suite_end(root_path / '_x.suite'),
            reporting_output.suite_begin(root_path / 'main.suite'),
            reporting_output.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return 0


class ReferencesToSuiteFilesThatMatchesFilesTypeNegatedCharacterRange(
    main_program_check_for_test_suite.SetupWithoutPreprocessor):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[suites]',
                                              '_[!a-bx].suite'])),
            empty_file('_b.suite'),
            empty_file('_x.suite'),
            empty_file('_a.suite'),
            empty_file('_c.suite'),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return [
            reporting_output.suite_begin(root_path / '_c.suite'),
            reporting_output.suite_end(root_path / '_c.suite'),
            reporting_output.suite_begin(root_path / 'main.suite'),
            reporting_output.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return 0


class ReferencesToCaseFilesThatMatchesFilesTypeNegatedCharacterRange(
    main_program_check_for_test_suite.SetupWithoutPreprocessor):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return [
            reporting_output.suite_begin(root_path / 'main.suite'),
            reporting_output.case(root_path / '_c.case', FullResultStatus.PASS.name),
            reporting_output.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return 0


class ReferencesToCaseFilesInAnyDirectSubDir(main_program_check_for_test_suite.SetupWithoutPreprocessor):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return [
            reporting_output.suite_begin(root_path / 'main.suite'),
            reporting_output.case(root_path / 'sub-dir-1' / 'a.case', FullResultStatus.PASS.name),
            reporting_output.case(root_path / 'sub-dir-1' / 'b.case', FullResultStatus.PASS.name),
            reporting_output.case(root_path / 'sub-dir-2' / 'x.case', FullResultStatus.PASS.name),
            reporting_output.case(root_path / 'sub-dir-2' / 'y.case', FullResultStatus.PASS.name),
            reporting_output.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return 0


class ReferencesToSuiteFilesInAnyDirectSubDir(main_program_check_for_test_suite.SetupWithoutPreprocessor):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return [
            reporting_output.suite_begin(root_path / 'sub-dir-1' / 'a.suite'),
            reporting_output.suite_end(root_path / 'sub-dir-1' / 'a.suite'),
            reporting_output.suite_begin(root_path / 'sub-dir-1' / 'b.suite'),
            reporting_output.suite_end(root_path / 'sub-dir-1' / 'b.suite'),
            reporting_output.suite_begin(root_path / 'sub-dir-2' / 'x.suite'),
            reporting_output.suite_end(root_path / 'sub-dir-2' / 'x.suite'),
            reporting_output.suite_begin(root_path / 'sub-dir-2' / 'y.suite'),
            reporting_output.suite_end(root_path / 'sub-dir-2' / 'y.suite'),
            reporting_output.suite_begin(root_path / 'main.suite'),
            reporting_output.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return 0


class ReferencesToCaseFilesInAnySubDir(main_program_check_for_test_suite.SetupWithoutPreprocessor):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return [
            reporting_output.suite_begin(root_path / 'main.suite'),
            reporting_output.case(root_path / '1.case', FullResultStatus.PASS.name),
            reporting_output.case(root_path / '2.case', FullResultStatus.PASS.name),
            reporting_output.case(root_path / 'sub-dir-1' / 'a.case', FullResultStatus.PASS.name),
            reporting_output.case(root_path / 'sub-dir-1' / 'b.case', FullResultStatus.PASS.name),
            reporting_output.case(root_path / 'sub-dir-1' / 'sub-dir-1-1' / '1-1.case', FullResultStatus.PASS.name),
            reporting_output.case(root_path / 'sub-dir-2' / 'x.case', FullResultStatus.PASS.name),
            reporting_output.case(root_path / 'sub-dir-2' / 'y.case', FullResultStatus.PASS.name),
            reporting_output.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return 0


class ReferencesToSuiteFilesInAnySubDir(main_program_check_for_test_suite.SetupWithoutPreprocessor):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return [
            reporting_output.suite_begin(root_path / '_1.suite'),
            reporting_output.suite_end(root_path / '_1.suite'),
            reporting_output.suite_begin(root_path / '_2.suite'),
            reporting_output.suite_end(root_path / '_2.suite'),
            reporting_output.suite_begin(root_path / 'sub-dir-1' / '_a.suite'),
            reporting_output.suite_end(root_path / 'sub-dir-1' / '_a.suite'),
            reporting_output.suite_begin(root_path / 'sub-dir-1' / '_b.suite'),
            reporting_output.suite_end(root_path / 'sub-dir-1' / '_b.suite'),
            reporting_output.suite_begin(root_path / 'sub-dir-1' / 'sub-dir-1-1' / '_1-1.suite'),
            reporting_output.suite_end(root_path / 'sub-dir-1' / 'sub-dir-1-1' / '_1-1.suite'),
            reporting_output.suite_begin(root_path / 'sub-dir-2' / '_x.suite'),
            reporting_output.suite_end(root_path / 'sub-dir-2' / '_x.suite'),
            reporting_output.suite_begin(root_path / 'sub-dir-2' / '_y.suite'),
            reporting_output.suite_end(root_path / 'sub-dir-2' / '_y.suite'),
            reporting_output.suite_begin(root_path / 'main.suite'),
            reporting_output.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return 0


class ReferencesToCaseFilesThatAreDirectories(main_program_check_for_test_suite.SetupWithoutPreprocessor):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return []

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return INVALID_SUITE_EXIT_CODE


class ReferencesToSuiteFilesThatAreDirectories(main_program_check_for_test_suite.SetupWithoutPreprocessor):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return []

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return INVALID_SUITE_EXIT_CODE


class ReferencesToCaseFilesInSubDirThatMatchesFiles(main_program_check_for_test_suite.SetupWithoutPreprocessor):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return [
            reporting_output.suite_begin(root_path / 'main.suite'),
            reporting_output.case(root_path / 'sub-dir-1' / 'a.case', FullResultStatus.PASS.name),
            reporting_output.case(root_path / 'sub-dir-1' / 'b.case', FullResultStatus.PASS.name),
            reporting_output.case(root_path / 'sub-dir-2' / '11.case', FullResultStatus.PASS.name),
            reporting_output.case(root_path / 'sub-dir-2' / '22.case', FullResultStatus.PASS.name),
            reporting_output.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return 0
