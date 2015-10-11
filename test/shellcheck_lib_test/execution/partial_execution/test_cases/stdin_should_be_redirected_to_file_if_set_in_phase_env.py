"""
Checks that output to stdout, stderr and the exit code are saved in the correct locations.
"""
import unittest

from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.act import ActPhaseInstruction, PhaseEnvironmentForScriptGeneration
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib_test.execution.util import utils
from shellcheck_lib_test.execution.util import py_unit_test_case
from shellcheck_lib_test.execution.util.py_unit_test_case import TestCaseWithCommonDefaultForSetupAssertCleanup
from shellcheck_lib.test_case.instruction import common

INPUT_TMP_FILE = 'input.txt'

EXPECTED_EXIT_CODE = 0
TEXT_ON_STDIN = 'on stdin'
EXPECTED_CONTENTS_OF_STDERR = ''


class TestCaseDocument(TestCaseWithCommonDefaultForSetupAssertCleanup):
    def _setup_phase(self) -> list:
        return [
            self._next_instruction_line(
                PyCommandThatStoresStringInFileInCurrentDirectory(INPUT_TMP_FILE,
                                                                  TEXT_ON_STDIN)),
            self._next_instruction_line(InstructionThatSetsStdinFileName(INPUT_TMP_FILE)),
        ]

    def _act_phase(self) -> list:
        return [
            self._next_instruction_line(StatementsThatCopiesStdinToStdout())
        ]


def assertions(utc: unittest.TestCase,
               actual: py_unit_test_case.Result):
    utils.assert_is_file_with_contents(
        utc,
        actual.execution_directory_structure.result.exitcode_file,
        str(EXPECTED_EXIT_CODE))
    utils.assert_is_file_with_contents(
        utc,
        actual.execution_directory_structure.result.std.stdout_file,
        TEXT_ON_STDIN)
    utils.assert_is_file_with_contents(
        utc,
        actual.execution_directory_structure.result.std.stderr_file,
        EXPECTED_CONTENTS_OF_STDERR)


class PyCommandThatStoresStringInFileInCurrentDirectory(SetupPhaseInstruction):
    def __init__(self,
                 file_base_name: str,
                 text_to_store: str):
        super().__init__()
        self.__file_base_name = file_base_name
        self.__text_to_store = text_to_store

    def pre_validate(self,
                     global_environment: common.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             os_services: OsServices,
             environment: common.GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder):
        with open(self.__file_base_name, 'w') as f:
            f.write(self.__text_to_store)
        return svh.new_svh_success()

    def post_validate(self, global_environment: common.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()


class StatementsThatCopiesStdinToStdout(ActPhaseInstruction):
    def __init__(self):
        super().__init__()

    def validate(self, global_environment: common.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             global_environment: common.GlobalEnvironmentForPostEdsPhase,
             phase_environment: PhaseEnvironmentForScriptGeneration) \
            -> sh.SuccessOrHardError:
        statements = [
            'import sys',
            'sys.stdout.write(sys.stdin.read())',
        ]
        phase_environment.append.raw_script_statements(statements)
        return svh.new_svh_success()


class InstructionThatSetsStdinFileName(SetupPhaseInstruction):
    def __init__(self,
                 file_name: str):
        super().__init__()
        self.__file_name = file_name

    def pre_validate(self,
                     global_environment: common.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             os_services: OsServices,
             environment: common.GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        settings_builder.stdin_file_name = self.__file_name
        return sh.new_sh_success()

    def post_validate(self,
                      global_environment: common.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()
