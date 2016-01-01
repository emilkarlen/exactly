"""
Checks that output to stdout, stderr and the exit code are saved in the correct locations.
"""
import unittest

from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections import common
from shellcheck_lib.test_case.sections.act.instruction import ActPhaseInstruction, PhaseEnvironmentForScriptGeneration
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder
from shellcheck_lib_test.execution.partial_execution import test_resources
from shellcheck_lib_test.execution.partial_execution.test_resources import \
    TestCaseWithCommonDefaultForSetupAssertCleanup
from shellcheck_lib_test.test_resources.eds_test import ResultFilesCheck

INPUT_TMP_FILE = 'input.txt'

EXPECTED_EXIT_CODE = 0
TEXT_ON_STDIN = 'on stdin'
EXPECTED_CONTENTS_OF_STDERR = ''


class TestCaseDocumentThatSetsStdinFileName(TestCaseWithCommonDefaultForSetupAssertCleanup):
    def _setup_phase(self) -> list:
        return self.instruction_line_constructor.apply_list([
            PyCommandThatStoresStringInFileInCurrentDirectory(INPUT_TMP_FILE,
                                                              TEXT_ON_STDIN),
            InstructionThatSetsStdinFileName(INPUT_TMP_FILE)
        ])

    def _act_phase(self) -> list:
        return self.instruction_line_constructor.apply_list([
            GenerateStatementsThatCopiesStdinToStdout()
        ])


class TestCaseDocumentThatSetsStdinContents(TestCaseWithCommonDefaultForSetupAssertCleanup):
    def _setup_phase(self) -> list:
        return self.instruction_line_constructor.apply_list([
            InstructionThatSetsStdinContents(TEXT_ON_STDIN),
        ])

    def _act_phase(self) -> list:
        return self.instruction_line_constructor.apply_list([
            GenerateStatementsThatCopiesStdinToStdout()
        ])


def assertions(utc: unittest.TestCase,
               actual: test_resources.Result):
    result_check = ResultFilesCheck(EXPECTED_EXIT_CODE,
                                    TEXT_ON_STDIN,
                                    EXPECTED_CONTENTS_OF_STDERR)
    result_check.apply(utc, actual.execution_directory_structure)


class PyCommandThatStoresStringInFileInCurrentDirectory(SetupPhaseInstruction):
    def __init__(self,
                 file_base_name: str,
                 text_to_store: str):
        super().__init__()
        self.__file_base_name = file_base_name
        self.__text_to_store = text_to_store

    def main(self,
             os_services: OsServices,
             environment: common.GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder):
        with open(self.__file_base_name, 'w') as f:
            f.write(self.__text_to_store)
        return svh.new_svh_success()


class GenerateStatementsThatCopiesStdinToStdout(ActPhaseInstruction):
    def __init__(self):
        super().__init__()

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

    def main(self,
             os_services: OsServices,
             environment: common.GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        settings_builder.stdin.file_name = self.__file_name
        return sh.new_sh_success()


class InstructionThatSetsStdinContents(SetupPhaseInstruction):
    def __init__(self,
                 contents: str):
        super().__init__()
        self.__contents = contents

    def main(self,
             os_services: OsServices,
             environment: common.GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        settings_builder.stdin.contents = self.__contents
        return sh.new_sh_success()
