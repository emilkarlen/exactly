"""
Test of test-infrastructure: instruction_check.
"""
import os
import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure

from shellcheck_lib.general import line_source

from shellcheck_lib.test_case.instruction.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep

from shellcheck_lib.test_case.instruction.result import sh

from shellcheck_lib.test_case.instruction.result import svh

from shellcheck_lib.test_case.instruction.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder
from shellcheck_lib_test.execution.full_execution.util.instruction_test_resources import \
    SetupPhaseInstructionThatReturns
from shellcheck_lib_test.instructions.setup.test_resources import instruction_check
from shellcheck_lib_test.instructions import utils
from shellcheck_lib_test.instructions.utils import SingleInstructionParserSource
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources import eds_contents_check
from shellcheck_lib_test.instructions.setup.test_resources import settings_check


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCases))
    return ret_val


if __name__ == '__main__':
    unittest.main()


class TestCases(instruction_check.TestCaseBase):
    def test_successful_flow(self):
        self._check(
            instruction_check.Flow(ParserThatGives(SUCCESSFUL_INSTRUCTION)),
            single_line_source())

    def test_fail_due_to_unexpected_result_from_pre_validation(self):
        with self.assertRaises(TestError):
            self._check(
                instruction_check.Flow(ParserThatGives(SUCCESSFUL_INSTRUCTION),
                                       expected_pre_validation_result=SvhRaisesTestError()),
                single_line_source())

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(TestError):
            self._check(
                instruction_check.Flow(ParserThatGives(SUCCESSFUL_INSTRUCTION),
                                       expected_main_result=ShRaisesTestError()),
                single_line_source())

    def test_fail_due_to_fail_of_side_effects_on_environment(self):
        with self.assertRaises(TestError):
            self._check(
                instruction_check.Flow(ParserThatGives(SUCCESSFUL_INSTRUCTION),
                                       expected_main_side_effects_on_environment=SettingsCheckRaisesTestError()),
                single_line_source())

    def test_fail_due_to_fail_of_side_effects_on_files(self):
        with self.assertRaises(TestError):
            self._check(
                instruction_check.Flow(ParserThatGives(SUCCESSFUL_INSTRUCTION),
                                       expected_main_side_effects_on_files=EdsContentsRaisesTestError()),
                single_line_source())

    def test_fail_due_to_unexpected_result_from_post_validation(self):
        with self.assertRaises(TestError):
            self._check(
                instruction_check.Flow(ParserThatGives(SUCCESSFUL_INSTRUCTION),
                                       expected_post_validation_result=SvhRaisesTestError()),
                single_line_source())

    def test_that_cwd_for_main_and_post_validation_is_test_root(self):
        self._check(
            instruction_check.Flow(ParserThatGives(InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot())),
            single_line_source())

class TestError(Exception):
    pass


class SvhRaisesTestError(svh_check.Assertion):
    def apply(self, put: unittest.TestCase, actual: svh.SuccessOrValidationErrorOrHardError):
        raise TestError()


class ShRaisesTestError(sh_check.Assertion):
    def apply(self, put: unittest.TestCase, actual: sh.SuccessOrHardError):
        raise TestError()


class EdsContentsRaisesTestError(eds_contents_check.Assertion):
    def apply(self, put: unittest.TestCase, eds: ExecutionDirectoryStructure):
        raise TestError()


class SettingsCheckRaisesTestError(settings_check.Assertion):
    def apply(self, put: unittest.TestCase,
              initial: SetupSettingsBuilder,
              actual_result: SetupSettingsBuilder):
        raise TestError()


def single_line_source() -> SingleInstructionParserSource:
    return utils.new_source('instruction name', 'instruction arguments')


class ParserThatGivesAnInstructionThatJustSucceeds(SingleInstructionParser):
    def apply(self, source: line_source.LineSequenceBuilder, instruction_argument: str) -> SetupPhaseInstruction:
        return SetupPhaseInstructionThatReturns(svh.new_svh_success(),
                                                sh.new_sh_success(),
                                                svh.new_svh_success())


SUCCESSFUL_INSTRUCTION = SetupPhaseInstructionThatReturns(svh.new_svh_success(),
                                                          sh.new_sh_success(),
                                                          svh.new_svh_success())


class ParserThatGives(SingleInstructionParser):
    def __init__(self,
                 instruction: SetupPhaseInstruction):
        self.instruction = instruction

    def apply(self, source: line_source.LineSequenceBuilder, instruction_argument: str) -> SetupPhaseInstruction:
        return self.instruction


class InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot(SetupPhaseInstruction):
    def pre_validate(self,
                     global_environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self, global_environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        self._raise_if_invalid_cwd(global_environment)
        return sh.new_sh_success()

    def post_validate(self,
                      global_environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        self._raise_if_invalid_cwd(global_environment)
        return svh.new_svh_success()

    @staticmethod
    def _raise_if_invalid_cwd(global_environment):
        cwd = os.getcwd()
        if cwd != str(global_environment.eds.test_root_dir):
            raise TestError()
