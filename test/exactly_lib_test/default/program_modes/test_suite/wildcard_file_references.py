"""
NOTE: These tests should not use MainProgramRunner, but should be normal (à la instruction test) integration tests
"""
import pathlib
import unittest
from typing import List

from exactly_lib.processing.exit_values import EXECUTION__PASS
from exactly_lib.test_suite import exit_values
from exactly_lib.util.string import lines_content
from exactly_lib_test.test_resources.files.file_structure import DirContents, Dir, File, empty_file
from exactly_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_without_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_suite.reporters.test_resources import simple_progress_reporter_output
from exactly_lib_test.test_suite.reporters.test_resources.simple_progress_reporter_test_setup_base import \
    SetupWithReplacementOfVariableOutputWithPlaceholders


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(
        tests_for_setup_without_preprocessor(TESTS_WITH_WILDCARD_FILE_REFERENCES_TO_CASE_FILES,
                                             main_program_runner))
    ret_val.addTest(
        tests_for_setup_without_preprocessor(TESTS_WITH_WILDCARD_FILE_REFERENCES_TO_SUITE_FILES,
                                             main_program_runner))
    return ret_val


def suite_for_running_main_program_internally() -> unittest.TestSuite:
    from exactly_lib_test.default.test_resources.internal_main_program_runner import \
        main_program_runner_with_default_setup__in_same_process

    return suite_for(main_program_runner_with_default_setup__in_same_process())


class ReferencesToCaseFilesThatMatchesNoFiles(SetupWithReplacementOfVariableOutputWithPlaceholders):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              '?.case'])),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToSuiteFilesThatMatchesNoFiles(SetupWithReplacementOfVariableOutputWithPlaceholders):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[suites]',
                                              '?.suite'])),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToCaseFilesThatMatchesFilesTypeQuestionMark(SetupWithReplacementOfVariableOutputWithPlaceholders):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              '?.case'])),
            empty_file('b.case'),
            empty_file('a.case'),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.case(root_path / 'a.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'b.case', EXECUTION__PASS.exit_identifier),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToSuiteFilesThatMatchesFilesTypeQuestionMark(
    SetupWithReplacementOfVariableOutputWithPlaceholders):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[suites]',
                                              '?.suite'])),
            empty_file('b.suite'),
            empty_file('a.suite'),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'a.suite'),
            expected_line.suite_end(root_path / 'a.suite'),
            expected_line.suite_begin(root_path / 'b.suite'),
            expected_line.suite_end(root_path / 'b.suite'),
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToCaseFilesThatMatchesFilesTypeCharacterRange(SetupWithReplacementOfVariableOutputWithPlaceholders):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.case(root_path / '_a.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / '_b.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / '_x.case', EXECUTION__PASS.exit_identifier),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToSuiteFilesThatMatchesFilesTypeCharacterRange(SetupWithReplacementOfVariableOutputWithPlaceholders):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
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

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToSuiteFilesThatMatchesFilesTypeNegatedCharacterRange(
    SetupWithReplacementOfVariableOutputWithPlaceholders):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / '_c.suite'),
            expected_line.suite_end(root_path / '_c.suite'),
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToCaseFilesThatMatchesFilesTypeNegatedCharacterRange(
    SetupWithReplacementOfVariableOutputWithPlaceholders):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.case(root_path / '_c.case', EXECUTION__PASS.exit_identifier),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToCaseFilesInAnyDirectSubDir(SetupWithReplacementOfVariableOutputWithPlaceholders):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.case(root_path / 'sub-dir-1' / 'a.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'sub-dir-1' / 'b.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'sub-dir-2' / 'x.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'sub-dir-2' / 'y.case', EXECUTION__PASS.exit_identifier),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToSuiteFilesInAnyDirectSubDir(SetupWithReplacementOfVariableOutputWithPlaceholders):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
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

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToCaseFilesInAnySubDir(SetupWithReplacementOfVariableOutputWithPlaceholders):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
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

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToSuiteFilesInAnySubDir(SetupWithReplacementOfVariableOutputWithPlaceholders):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
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

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


class ReferencesToCaseFilesThatAreDirectories(SetupWithReplacementOfVariableOutputWithPlaceholders):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> List[str]:
        return []

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_invalid_suite(root_path, exit_values.INVALID_SUITE)

    def expected_exit_code(self) -> int:
        return exit_values.INVALID_SUITE.exit_code


class ReferencesToSuiteFilesThatAreDirectories(SetupWithReplacementOfVariableOutputWithPlaceholders):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> List[str]:
        return []

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_invalid_suite(root_path, exit_values.INVALID_SUITE)

    def expected_exit_code(self) -> int:
        return exit_values.INVALID_SUITE.exit_code


class ReferencesToCaseFilesInSubDirThatMatchesFiles(SetupWithReplacementOfVariableOutputWithPlaceholders):
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

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.case(root_path / 'sub-dir-1' / 'a.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'sub-dir-1' / 'b.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'sub-dir-2' / '11.case', EXECUTION__PASS.exit_identifier),
            expected_line.case(root_path / 'sub-dir-2' / '22.case', EXECUTION__PASS.exit_identifier),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> List[str]:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


TESTS_WITH_WILDCARD_FILE_REFERENCES_TO_CASE_FILES = [
    ReferencesToCaseFilesThatMatchesNoFiles(),
    ReferencesToCaseFilesThatAreDirectories(),
    ReferencesToCaseFilesThatMatchesFilesTypeQuestionMark(),
    ReferencesToCaseFilesThatMatchesFilesTypeCharacterRange(),
    ReferencesToCaseFilesThatMatchesFilesTypeNegatedCharacterRange(),
    ReferencesToCaseFilesInSubDirThatMatchesFiles(),
    ReferencesToCaseFilesInAnyDirectSubDir(),
    ReferencesToCaseFilesInAnySubDir(),
]

TESTS_WITH_WILDCARD_FILE_REFERENCES_TO_SUITE_FILES = [
    ReferencesToSuiteFilesThatAreDirectories(),
    ReferencesToSuiteFilesThatMatchesFilesTypeQuestionMark(),
    ReferencesToSuiteFilesThatMatchesFilesTypeCharacterRange(),
    ReferencesToSuiteFilesThatMatchesFilesTypeNegatedCharacterRange(),
    ReferencesToSuiteFilesInAnyDirectSubDir(),
    ReferencesToSuiteFilesInAnySubDir(),
]

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite_for_running_main_program_internally())
