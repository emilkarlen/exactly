"""
Test of test-infrastructure: instruction_check.
"""
import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib_test.execution.full_execution.util.instruction_test_resources import \
    SetupPhaseInstructionThatReturns
from shellcheck_lib.test_case.sections import common
from shellcheck_lib_test.instructions.test_resources import utils
from shellcheck_lib_test.instructions.test_resources.test_of_test_framework_utils import ParserThatGives
from shellcheck_lib_test.instructions.setup.test_resources import instruction_check
from shellcheck_lib_test.instructions.test_resources import test_of_test_framework_utils as test_misc
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
        with self.assertRaises(test_misc.TestError):
            self._check(
                instruction_check.Flow(ParserThatGives(SUCCESSFUL_INSTRUCTION),
                                       expected_pre_validation_result=test_misc.SvhRaisesTestError()),
                single_line_source())

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                instruction_check.Flow(ParserThatGives(SUCCESSFUL_INSTRUCTION),
                                       expected_main_result=test_misc.ShRaisesTestError()),
                single_line_source())

    def test_fail_due_to_fail_of_side_effects_on_environment(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                instruction_check.Flow(ParserThatGives(SUCCESSFUL_INSTRUCTION),
                                       expected_main_side_effects_on_environment=SettingsCheckRaisesTestError()),
                single_line_source())

    def test_fail_due_to_fail_of_side_effects_on_files(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                instruction_check.Flow(ParserThatGives(SUCCESSFUL_INSTRUCTION),
                                       expected_main_side_effects_on_files=test_misc.EdsContentsRaisesTestError()),
                single_line_source())

    def test_fail_due_to_unexpected_result_from_post_validation(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                instruction_check.Flow(ParserThatGives(SUCCESSFUL_INSTRUCTION),
                                       expected_post_validation_result=test_misc.SvhRaisesTestError()),
                single_line_source())

    def test_that_cwd_for_main_and_post_validation_is_test_root(self):
        self._check(
            instruction_check.Flow(ParserThatGives(InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot())),
            single_line_source())


class SettingsCheckRaisesTestError(settings_check.Assertion):
    def apply(self, put: unittest.TestCase,
              environment: common.GlobalEnvironmentForPostEdsPhase,
              initial: SetupSettingsBuilder,
              actual_result: SetupSettingsBuilder):
        raise test_misc.TestError()


def single_line_source() -> SingleInstructionParserSource:
    return utils.new_source('instruction name', 'instruction arguments')


SUCCESSFUL_INSTRUCTION = SetupPhaseInstructionThatReturns(svh.new_svh_success(),
                                                          sh.new_sh_success(),
                                                          svh.new_svh_success())


class InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot(SetupPhaseInstruction):
    def pre_validate(self,
                     global_environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        test_misc.raise_test_error_if_cwd_is_not_test_root(environment.eds)
        return sh.new_sh_success()

    def post_validate(self,
                      global_environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        test_misc.raise_test_error_if_cwd_is_not_test_root(global_environment.eds)
        return svh.new_svh_success()
