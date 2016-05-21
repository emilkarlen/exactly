import unittest

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.execution.partial_execution.test_resources.recording import validate_pre_eds_utils
from exactly_lib_test.execution.partial_execution.test_resources.test_case_generator import PartialPhase
from exactly_lib_test.execution.test_resources import instruction_test_resources as test
from exactly_lib_test.execution.test_resources.instruction_test_resources import do_raise, do_return


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTests(validate_pre_eds_utils.suite_for(conf)
                     for conf in _instruction_validation_invocations())
    return ret_val


class ConfigForSetupValidatePreEds(validate_pre_eds_utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.SETUP,
                         phase_step.SETUP__VALIDATE_PRE_EDS,
                         expected_steps=[phase_step.SETUP__VALIDATE_PRE_EDS])

    def instruction_that_returns(self, return_value: svh.SuccessOrValidationErrorOrHardError) -> TestCaseInstruction:
        return test.setup_phase_instruction_that(
                validate_pre_eds=do_return(return_value))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.setup_phase_instruction_that(validate_pre_eds=do_raise(exception))


class ConfigForActValidatePreEds(validate_pre_eds_utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.ACT,
                         phase_step.ACT__VALIDATE_PRE_EDS,
                         expected_steps=[phase_step.SETUP__VALIDATE_PRE_EDS,
                                         phase_step.SETUP__VALIDATE_PRE_EDS,
                                         phase_step.ACT__VALIDATE_PRE_EDS])

    def instruction_that_returns(self, return_value: svh.SuccessOrValidationErrorOrHardError) -> TestCaseInstruction:
        return test.act_phase_instruction_that(
                validate_pre_eds=do_return(return_value))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.act_phase_instruction_that(validate_pre_eds=do_raise(exception))


class ConfigForBeforeAssertValidatePreEds(validate_pre_eds_utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.BEFORE_ASSERT,
                         phase_step.BEFORE_ASSERT__VALIDATE_PRE_EDS,
                         expected_steps=[phase_step.SETUP__VALIDATE_PRE_EDS,
                                         phase_step.SETUP__VALIDATE_PRE_EDS,
                                         phase_step.ACT__VALIDATE_PRE_EDS,
                                         phase_step.ACT__VALIDATE_PRE_EDS,
                                         phase_step.BEFORE_ASSERT__VALIDATE_PRE_EDS])

    def instruction_that_returns(self, return_value: svh.SuccessOrValidationErrorOrHardError) -> TestCaseInstruction:
        return test.before_assert_phase_instruction_that(
                validate_pre_eds=do_return(return_value))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.before_assert_phase_instruction_that(validate_pre_eds=do_raise(exception))


class ConfigForAssertValidatePreEds(validate_pre_eds_utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.ASSERT,
                         phase_step.ASSERT__VALIDATE_PRE_EDS,
                         expected_steps=[phase_step.SETUP__VALIDATE_PRE_EDS,
                                         phase_step.SETUP__VALIDATE_PRE_EDS,
                                         phase_step.ACT__VALIDATE_PRE_EDS,
                                         phase_step.ACT__VALIDATE_PRE_EDS,
                                         phase_step.BEFORE_ASSERT__VALIDATE_PRE_EDS,
                                         phase_step.BEFORE_ASSERT__VALIDATE_PRE_EDS,
                                         phase_step.ASSERT__VALIDATE_PRE_EDS])

    def instruction_that_returns(self, return_value: svh.SuccessOrValidationErrorOrHardError) -> TestCaseInstruction:
        return test.assert_phase_instruction_that(
                validate_pre_eds=do_return(return_value))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.assert_phase_instruction_that(validate_pre_eds=do_raise(exception))


class ConfigForCleanupValidatePreEds(validate_pre_eds_utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.CLEANUP,
                         phase_step.CLEANUP__VALIDATE_PRE_EDS,
                         expected_steps=[phase_step.SETUP__VALIDATE_PRE_EDS,
                                         phase_step.SETUP__VALIDATE_PRE_EDS,
                                         phase_step.ACT__VALIDATE_PRE_EDS,
                                         phase_step.ACT__VALIDATE_PRE_EDS,
                                         phase_step.BEFORE_ASSERT__VALIDATE_PRE_EDS,
                                         phase_step.BEFORE_ASSERT__VALIDATE_PRE_EDS,
                                         phase_step.ASSERT__VALIDATE_PRE_EDS,
                                         phase_step.ASSERT__VALIDATE_PRE_EDS,
                                         phase_step.CLEANUP__VALIDATE_PRE_EDS])

    def instruction_that_returns(self, return_value: svh.SuccessOrValidationErrorOrHardError) -> TestCaseInstruction:
        return test.cleanup_phase_instruction_that(
                validate_pre_eds=do_return(return_value))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.cleanup_phase_instruction_that(validate_pre_eds=do_raise(exception))


def _instruction_validation_invocations() -> list:
    return [ConfigForSetupValidatePreEds(),
            ConfigForActValidatePreEds(),
            ConfigForBeforeAssertValidatePreEds(),
            ConfigForAssertValidatePreEds(),
            ConfigForCleanupValidatePreEds(),
            ]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
