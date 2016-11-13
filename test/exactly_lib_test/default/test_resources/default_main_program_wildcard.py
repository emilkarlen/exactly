import pathlib

from exactly_lib.execution.exit_values import EXECUTION__PASS
from exactly_lib.test_suite import exit_values
from exactly_lib.util.string import lines_content
from exactly_lib_test.default.test_resources import suite_reporting_output
from exactly_lib_test.test_resources.file_structure import DirContents, Dir, File, empty_file
from exactly_lib_test.test_resources.main_program import main_program_check_for_test_suite


class ReferencesToCaseFilesThatMatchesNoFiles(main_program_check_for_test_suite.SetupWithoutPreprocessorWithTestActor):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              '?.case'])),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToSuiteFilesThatMatchesNoFiles(main_program_check_for_test_suite.SetupWithoutPreprocessorWithTestActor):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[suites]',
                                              '?.suite'])),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToCaseFilesThatMatchesFilesTypeQuestionMark(
    main_program_check_for_test_suite.SetupWithoutPreprocessorWithTestActor):
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
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.case(root_path / 'a.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'b.case', EXECUTION__PASS.exit_identifier),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToSuiteFilesThatMatchesFilesTypeQuestionMark(
    main_program_check_for_test_suite.SetupWithoutPreprocessorWithTestActor):
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
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'a.suite'),
            expected_line.suite_end(root_path / 'a.suite'),
            expected_line.suite_begin(root_path / 'b.suite'),
            expected_line.suite_end(root_path / 'b.suite'),
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToCaseFilesThatMatchesFilesTypeCharacterRange(
    main_program_check_for_test_suite.SetupWithoutPreprocessorWithTestActor):
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
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.case(root_path / '_a.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / '_b.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / '_x.case', EXECUTION__PASS.exit_identifier),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToSuiteFilesThatMatchesFilesTypeCharacterRange(
    main_program_check_for_test_suite.SetupWithoutPreprocessorWithTestActor):
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
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / '_a.suite'),
            expected_line.suite_end(root_path / '_a.suite'),
            expected_line.suite_begin(root_path / '_b.suite'),
            expected_line.suite_end(root_path / '_b.suite'),
            expected_line.suite_begin(root_path / '_x.suite'),
            expected_line.suite_end(root_path / '_x.suite'),
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToSuiteFilesThatMatchesFilesTypeNegatedCharacterRange(
    main_program_check_for_test_suite.SetupWithoutPreprocessorWithTestActor):
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
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / '_c.suite'),
            expected_line.suite_end(root_path / '_c.suite'),
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToCaseFilesThatMatchesFilesTypeNegatedCharacterRange(
    main_program_check_for_test_suite.SetupWithoutPreprocessorWithTestActor):
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
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.case(root_path / '_c.case', EXECUTION__PASS.exit_identifier),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToCaseFilesInAnyDirectSubDir(main_program_check_for_test_suite.SetupWithoutPreprocessorWithTestActor):
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
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.case(root_path / 'sub-dir-1' / 'a.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'sub-dir-1' / 'b.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'sub-dir-2' / 'x.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'sub-dir-2' / 'y.case', EXECUTION__PASS.exit_identifier),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToSuiteFilesInAnyDirectSubDir(main_program_check_for_test_suite.SetupWithoutPreprocessorWithTestActor):
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
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'sub-dir-1' / 'a.suite'),
            expected_line.suite_end(root_path / 'sub-dir-1' / 'a.suite'),
            expected_line.suite_begin(root_path / 'sub-dir-1' / 'b.suite'),
            expected_line.suite_end(root_path / 'sub-dir-1' / 'b.suite'),
            expected_line.suite_begin(root_path / 'sub-dir-2' / 'x.suite'),
            expected_line.suite_end(root_path / 'sub-dir-2' / 'x.suite'),
            expected_line.suite_begin(root_path / 'sub-dir-2' / 'y.suite'),
            expected_line.suite_end(root_path / 'sub-dir-2' / 'y.suite'),
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToCaseFilesInAnySubDir(main_program_check_for_test_suite.SetupWithoutPreprocessorWithTestActor):
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
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.case(root_path / '1.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / '2.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'sub-dir-1' / 'a.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'sub-dir-1' / 'b.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'sub-dir-1' / 'sub-dir-1-1' / '1-1.case',
                                        EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'sub-dir-2' / 'x.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'sub-dir-2' / 'y.case', EXECUTION__PASS.exit_identifier),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToSuiteFilesInAnySubDir(main_program_check_for_test_suite.SetupWithoutPreprocessorWithTestActor):
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
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / '_1.suite'),
            expected_line.suite_end(root_path / '_1.suite'),
            expected_line.suite_begin(root_path / '_2.suite'),
            expected_line.suite_end(root_path / '_2.suite'),
            expected_line.suite_begin(root_path / 'sub-dir-1' / '_a.suite'),
            expected_line.suite_end(root_path / 'sub-dir-1' / '_a.suite'),
            expected_line.suite_begin(root_path / 'sub-dir-1' / '_b.suite'),
            expected_line.suite_end(root_path / 'sub-dir-1' / '_b.suite'),
            expected_line.suite_begin(root_path / 'sub-dir-1' / 'sub-dir-1-1' / '_1-1.suite'),
            expected_line.suite_end(root_path / 'sub-dir-1' / 'sub-dir-1-1' / '_1-1.suite'),
            expected_line.suite_begin(root_path / 'sub-dir-2' / '_x.suite'),
            expected_line.suite_end(root_path / 'sub-dir-2' / '_x.suite'),
            expected_line.suite_begin(root_path / 'sub-dir-2' / '_y.suite'),
            expected_line.suite_end(root_path / 'sub-dir-2' / '_y.suite'),
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToCaseFilesThatAreDirectories(main_program_check_for_test_suite.SetupWithoutPreprocessorWithTestActor):
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
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return expected_line.summary_for_invalid_suite(root_path, exit_values.INVALID_SUITE)

    def expected_exit_code(self) -> int:
        return exit_values.INVALID_SUITE.exit_code


class ReferencesToSuiteFilesThatAreDirectories(main_program_check_for_test_suite.SetupWithoutPreprocessorWithTestActor):
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
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return expected_line.summary_for_invalid_suite(root_path, exit_values.INVALID_SUITE)

    def expected_exit_code(self) -> int:
        return exit_values.INVALID_SUITE.exit_code


class ReferencesToCaseFilesInSubDirThatMatchesFiles(
    main_program_check_for_test_suite.SetupWithoutPreprocessorWithTestActor):
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
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.case(root_path / 'sub-dir-1' / 'a.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'sub-dir-1' / 'b.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'sub-dir-2' / '11.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'sub-dir-2' / '22.case', EXECUTION__PASS.exit_identifier),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = suite_reporting_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code
