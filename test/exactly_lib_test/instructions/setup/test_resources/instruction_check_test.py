"""
Test of test-infrastructure: instruction_check.
"""
import unittest

import exactly_lib_test.test_resources.parse
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib_test.execution.test_resources.instruction_test_resources import \
    setup_phase_instruction_that
from exactly_lib_test.instructions.setup.test_resources import instruction_check
from exactly_lib_test.instructions.setup.test_resources import settings_check
from exactly_lib_test.instructions.setup.test_resources.instruction_check import Arrangement, is_success, Expectation
from exactly_lib_test.instructions.test_resources import test_of_test_framework_utils as test_misc
from exactly_lib_test.instructions.test_resources.test_of_test_framework_utils import ParserThatGives


class TestCases(instruction_check.TestCaseBase):
    def test_successful_flow(self):
        self._check(ParserThatGives(SUCCESSFUL_INSTRUCTION),
                    single_line_source(),
                    Arrangement(),
                    is_success())

    def test_fail_due_to_unexpected_result_from_pre_validation(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                    ParserThatGives(SUCCESSFUL_INSTRUCTION),
                    single_line_source(),
                    Arrangement(),
                    Expectation(pre_validation_result=test_misc.SvhRaisesTestError())
            )

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                    ParserThatGives(SUCCESSFUL_INSTRUCTION),
                    single_line_source(),
                    Arrangement(),
                    Expectation(main_result=test_misc.ShRaisesTestError())
            )

    def test_fail_due_to_fail_of_side_effects_on_environment(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                    ParserThatGives(SUCCESSFUL_INSTRUCTION),
                    single_line_source(),
                    Arrangement(),
                    Expectation(main_side_effects_on_environment=SettingsCheckRaisesTestError())
            )

    def test_fail_due_to_fail_of_side_effects_on_files(self):
        with self.assertRaises(test_misc.TestError):
            self._check(ParserThatGives(SUCCESSFUL_INSTRUCTION),
                        single_line_source(),
                        Arrangement(),
                        Expectation(main_side_effects_on_files=test_misc.EdsContentsRaisesTestError()))

    def test_fail_due_to_unexpected_result_from_post_validation(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                    ParserThatGives(SUCCESSFUL_INSTRUCTION),
                    single_line_source(),
                    Arrangement(),
                    Expectation(post_validation_result=test_misc.SvhRaisesTestError())
            )

    def test_fail_due_to_side_effects_check(self):
        with self.assertRaises(test_misc.TestError):
            self._check(ParserThatGives(SUCCESSFUL_INSTRUCTION),
                        single_line_source(),
                        Arrangement(),
                        Expectation(side_effects_check=test_misc.SideEffectsCheckThatRaisesTestError())
                        )

    def test_that_cwd_for_main_and_post_validation_is_test_root(self):
        self._check(ParserThatGives(InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot()),
                    single_line_source(),
                    Arrangement(),
                    Expectation()
                    )


class SettingsCheckRaisesTestError(settings_check.Assertion):
    def apply(self, put: unittest.TestCase,
              environment: common.GlobalEnvironmentForPostEdsPhase,
              initial: SetupSettingsBuilder,
              actual_result: SetupSettingsBuilder):
        raise test_misc.TestError()


def single_line_source() -> SingleInstructionParserSource:
    return exactly_lib_test.test_resources.parse.new_source2('instruction arguments')


SUCCESSFUL_INSTRUCTION = setup_phase_instruction_that()


class InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot(SetupPhaseInstruction):
    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        test_misc.raise_test_error_if_cwd_is_not_test_root(environment.eds)
        return sh.new_sh_success()

    def validate_post_setup(self,
                            environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        test_misc.raise_test_error_if_cwd_is_not_test_root(environment.eds)
        return svh.new_svh_success()


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCases))
    return ret_val


if __name__ == '__main__':
    unittest.main()
