import pathlib
import unittest
from typing import List

from exactly_lib.processing import exit_values
from exactly_lib.section_document.syntax import LINE_COMMENT_MARKER
from exactly_lib.util.string import lines_content
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup__in_same_process
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement
from exactly_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_without_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_check_for_test_case import \
    SetupWithoutPreprocessorAndDefaultActor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.process import SubProcessResultInfo
from exactly_lib_test.test_resources.value_assertions.process_result_info_assertions import \
    process_result_for_exit_value
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return tests_for_setup_without_preprocessor(TESTS, main_program_runner)


def suite() -> unittest.TestSuite:
    return suite_for(main_program_runner_with_default_setup__in_same_process())


class DefaultActorConfShouldSucceedWhenActPhaseIsEmpty(SetupWithoutPreprocessorAndDefaultActor):
    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def test_case(self) -> str:
        return ''


class DefaultActorConfShouldSucceedWhenActPhaseIsJustSpace(SetupWithoutPreprocessorAndDefaultActor):
    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def test_case(self) -> str:
        return lines_content([
            '',
            '    ',
            '  ',
        ])


class DefaultActorConfShouldSucceedWhenActPhaseIsJustSpaceOrComments(SetupWithoutPreprocessorAndDefaultActor):
    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def test_case(self) -> str:
        return lines_content([
            LINE_COMMENT_MARKER + ' a comment',
            '  ',
        ])


class DefaultActorConfShouldSucceedWhenActPhaseIsASingleCommandLineOfAnExecutableProgramRelHds(
    SetupWithoutPreprocessorAndDefaultActor):
    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def _additional_files_in_file_structure(self, root_path: pathlib.Path) -> List[FileSystemElement]:
        return [
            fs.python_executable_file('system-under-test',
                                      PYTHON_PROGRAM_THAT_EXISTS_WITH_STATUS_0)
        ]

    def test_case(self) -> str:
        return lines_content(['system-under-test'])


class DefaultActorConfShouldFailWhenActPhaseIsMultipleCommandLines(
    SetupWithoutPreprocessorAndDefaultActor):
    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
        return process_result_for_exit_value(exit_values.EXECUTION__VALIDATION_ERROR)

    def _additional_files_in_file_structure(self, root_path: pathlib.Path) -> List[FileSystemElement]:
        return [
            fs.python_executable_file('system-under-test',
                                      PYTHON_PROGRAM_THAT_EXISTS_WITH_STATUS_0)
        ]

    def test_case(self) -> str:
        return lines_content(['system-under-test',
                              'system-under-test'])


TESTS = [
    DefaultActorConfShouldSucceedWhenActPhaseIsEmpty(),
    DefaultActorConfShouldSucceedWhenActPhaseIsJustSpace(),
    DefaultActorConfShouldSucceedWhenActPhaseIsJustSpaceOrComments(),
    DefaultActorConfShouldSucceedWhenActPhaseIsASingleCommandLineOfAnExecutableProgramRelHds(),
    DefaultActorConfShouldFailWhenActPhaseIsMultipleCommandLines(),
]

PYTHON_PROGRAM_THAT_EXISTS_WITH_STATUS_0 = lines_content(['import sys',
                                                          'sys.exit(0)'])

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
