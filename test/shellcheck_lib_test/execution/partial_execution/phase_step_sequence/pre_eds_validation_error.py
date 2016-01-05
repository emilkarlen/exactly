import unittest

from shellcheck_lib.execution import phase_step
from shellcheck_lib.test_case.sections.common import TestCaseInstruction
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.execution.partial_execution.test_resources.recording import validate_pre_eds_utils
from shellcheck_lib_test.execution.partial_execution.test_resources.test_case_generator import PartialPhase
from shellcheck_lib_test.execution.test_resources import instruction_test_resources as test
from shellcheck_lib_test.execution.test_resources.instruction_test_resources import do_raise, do_return


class ConfigForSetupValidatePreEds(validate_pre_eds_utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.SETUP,
                         phase_step.SETUP_VALIDATE_PRE_EDS,
                         expected_steps=[phase_step.SETUP_VALIDATE_PRE_EDS])

    def instruction_that_returns(self, return_value: svh.SuccessOrValidationErrorOrHardError) -> TestCaseInstruction:
        return test.setup_phase_instruction_that(
                validate_pre_eds=do_return(return_value))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.setup_phase_instruction_that(validate_pre_eds=do_raise(exception))


class ConfigForActValidatePreEds(validate_pre_eds_utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.ACT,
                         phase_step.ACT_VALIDATE_PRE_EDS,
                         expected_steps=[phase_step.SETUP_VALIDATE_PRE_EDS,
                                         phase_step.ACT_VALIDATE_PRE_EDS])

    def instruction_that_returns(self, return_value: svh.SuccessOrValidationErrorOrHardError) -> TestCaseInstruction:
        return test.act_phase_instruction_that(
                validate_pre_eds=do_return(return_value))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.act_phase_instruction_that(validate_pre_eds=do_raise(exception))


class ConfigForBeforeAssertValidatePreEds(validate_pre_eds_utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.BEFORE_ASSERT,
                         phase_step.BEFORE_ASSERT_VALIDATE_PRE_EDS,
                         expected_steps=[phase_step.SETUP_VALIDATE_PRE_EDS,
                                         phase_step.ACT_VALIDATE_PRE_EDS,
                                         phase_step.BEFORE_ASSERT_VALIDATE_PRE_EDS])

    def instruction_that_returns(self, return_value: svh.SuccessOrValidationErrorOrHardError) -> TestCaseInstruction:
        return test.before_assert_phase_instruction_that(
                validate_pre_eds=do_return(return_value))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.before_assert_phase_instruction_that(validate_pre_eds=do_raise(exception))


class ConfigForAssertValidatePreEds(validate_pre_eds_utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.ASSERT,
                         phase_step.ASSERT_VALIDATE_PRE_EDS,
                         expected_steps=[phase_step.SETUP_VALIDATE_PRE_EDS,
                                         phase_step.ACT_VALIDATE_PRE_EDS,
                                         phase_step.BEFORE_ASSERT_VALIDATE_PRE_EDS,
                                         phase_step.ASSERT_VALIDATE_PRE_EDS])

    def instruction_that_returns(self, return_value: svh.SuccessOrValidationErrorOrHardError) -> TestCaseInstruction:
        return test.assert_phase_instruction_that(
                validate_pre_eds=do_return(return_value))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.assert_phase_instruction_that(validate_pre_eds=do_raise(exception))


class ConfigForCleanupValidatePreEds(validate_pre_eds_utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.CLEANUP,
                         phase_step.CLEANUP_VALIDATE_PRE_EDS,
                         expected_steps=[phase_step.SETUP_VALIDATE_PRE_EDS,
                                         phase_step.ACT_VALIDATE_PRE_EDS,
                                         phase_step.BEFORE_ASSERT_VALIDATE_PRE_EDS,
                                         phase_step.ASSERT_VALIDATE_PRE_EDS,
                                         phase_step.CLEANUP_VALIDATE_PRE_EDS])

    def instruction_that_returns(self, return_value: svh.SuccessOrValidationErrorOrHardError) -> TestCaseInstruction:
        return test.cleanup_phase_instruction_that(
                validate_pre_eds=do_return(return_value))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.cleanup_phase_instruction_that(validate_pre_eds=do_raise(exception))


def instruction_validation_invocations() -> list:
    return [ConfigForSetupValidatePreEds(),
            ConfigForActValidatePreEds(),
            ConfigForBeforeAssertValidatePreEds(),
            ConfigForAssertValidatePreEds(),
            ConfigForCleanupValidatePreEds(),
            ]


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTests(validate_pre_eds_utils.suite_for(conf)
                     for conf in instruction_validation_invocations())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
