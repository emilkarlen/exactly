import os
import unittest

from shellcheck_lib.test_case.instruction.result import sh
from shellcheck_lib.test_case.instruction.result import svh
from shellcheck_lib.execution import phases
from shellcheck_lib.general import line_source
from shellcheck_lib.test_case.instruction import common
from shellcheck_lib_test.execution.util import utils
from shellcheck_lib_test.execution.util import py_unit_test_case
from shellcheck_lib_test.execution.util.py_unit_test_case import TestCaseWithCommonDefaultForSetupAssertCleanup
import shellcheck_lib_test.util.model_utils
from shellcheck_lib.test_case.instruction.sections.act import ActPhaseInstruction, PhaseEnvironmentForScriptGeneration

HOME_DIR_HEADER = '# Home Dir: '
TEST_ROOT_DIR_HEADER = '# Test Root Dir: '


class TestCaseDocument(TestCaseWithCommonDefaultForSetupAssertCleanup):
    def _act_phase(self) -> list:
        return [
            shellcheck_lib_test.util.model_utils.new_instruction_element(
                line_source.Line(1, 'source for line one'),
                ActPhaseInstructionThatOutputsHomeDir()),
            shellcheck_lib_test.util.model_utils.new_comment_element(
                line_source.Line(2, 'comment on line two')),
            shellcheck_lib_test.util.model_utils.new_instruction_element(
                line_source.Line(3, 'source for line three'),
                ActPhaseInstructionThatOutputsTestRootDir()),
        ]


def assertions(utc: unittest.TestCase,
               actual: py_unit_test_case.Result):
    expected_base_name = phases.ACT.name + '.py'
    expected_dir = actual.partial_executor.execution_directory_structure.test_case_dir
    expected_file_path = expected_dir / expected_base_name

    home_dir_name = str(actual.home_dir_path)
    test_root_dir_name = str(actual.execution_directory_structure.test_root_dir)

    expected_contents = os.linesep.join(['# Line 1',
                                         '# source for line one',
                                         HOME_DIR_HEADER + home_dir_name,
                                         '# comment on line two',
                                         '# Line 3',
                                         '# source for line three',
                                         TEST_ROOT_DIR_HEADER + test_root_dir_name,
                                         ''])

    utils.assert_is_file_with_contents(utc,
                                       expected_file_path,
                                       expected_contents)


class ActPhaseInstructionThatOutputsHomeDir(ActPhaseInstruction):
    def validate(self, global_environment: common.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(
            self,
            global_environment: common.GlobalEnvironmentForPostEdsPhase,
            phase_environment: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        line = HOME_DIR_HEADER + str(global_environment.home_directory)
        phase_environment.append.raw_script_statement(line)
        return sh.new_sh_success()


class ActPhaseInstructionThatOutputsTestRootDir(ActPhaseInstruction):
    def validate(self, global_environment: common.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(
            self,
            global_environment: common.GlobalEnvironmentForPostEdsPhase,
            phase_environment: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        line = TEST_ROOT_DIR_HEADER + str(global_environment.eds.test_root_dir)
        phase_environment.append.raw_script_statement(line)
        return sh.new_sh_success()
