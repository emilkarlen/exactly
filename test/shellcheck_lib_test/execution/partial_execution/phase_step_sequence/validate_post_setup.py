import unittest

from shellcheck_lib.execution import phase_step
from shellcheck_lib.test_case.sections.common import TestCaseInstruction
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.execution.partial_execution.test_resources.recording import validate_post_setup_utils as utils
from shellcheck_lib_test.execution.partial_execution.test_resources.test_case_generator import PartialPhase
from shellcheck_lib_test.execution.test_resources import instruction_test_resources as test
from shellcheck_lib_test.execution.test_resources.execution_recording.phase_steps import PRE_EDS_VALIDATION_STEPS
from shellcheck_lib_test.execution.test_resources.instruction_test_resources import do_raise, do_return


class SetupConfig(utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.SETUP,
                         phase_step.SETUP_POST_VALIDATE,
                         expected_steps_before_validation=
                         PRE_EDS_VALIDATION_STEPS + [phase_step.SETUP_MAIN]
                         )

    def instruction_that_returns(self, return_value: svh.SuccessOrValidationErrorOrHardError) -> TestCaseInstruction:
        return test.setup_phase_instruction_that(
                validate_post_eds=do_return(return_value))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.setup_phase_instruction_that(validate_post_eds=do_raise(exception))


class ActConfig(utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.ACT,
                         phase_step.ACT_VALIDATE_POST_EDS,
                         expected_steps_before_validation=
                         PRE_EDS_VALIDATION_STEPS + [phase_step.SETUP_MAIN,
                                                     phase_step.SETUP_POST_VALIDATE]
                         )

    def instruction_that_returns(self, return_value: svh.SuccessOrValidationErrorOrHardError) -> TestCaseInstruction:
        return test.act_phase_instruction_that(
                validate_post_eds=do_return(return_value))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.act_phase_instruction_that(validate_post_eds=do_raise(exception))


class BeforeAssertConfig(utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.BEFORE_ASSERT,
                         phase_step.BEFORE_ASSERT_VALIDATE_POST_EDS,
                         expected_steps_before_validation=
                         PRE_EDS_VALIDATION_STEPS + [phase_step.SETUP_MAIN,
                                                     phase_step.SETUP_POST_VALIDATE,
                                                     phase_step.ACT_VALIDATE_POST_EDS]
                         )

    def instruction_that_returns(self, return_value: svh.SuccessOrValidationErrorOrHardError) -> TestCaseInstruction:
        return test.before_assert_phase_instruction_that(
                validate_post_eds=do_return(return_value))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.before_assert_phase_instruction_that(validate_post_eds=do_raise(exception))


class AssertConfig(utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.ASSERT,
                         phase_step.ASSERT_VALIDATE_POST_EDS,
                         expected_steps_before_validation=
                         PRE_EDS_VALIDATION_STEPS + [phase_step.SETUP_MAIN,
                                                     phase_step.SETUP_POST_VALIDATE,
                                                     phase_step.ACT_VALIDATE_POST_EDS,
                                                     phase_step.BEFORE_ASSERT_VALIDATE_POST_EDS,
                                                     ]
                         )

    def instruction_that_returns(self, return_value: svh.SuccessOrValidationErrorOrHardError) -> TestCaseInstruction:
        return test.assert_phase_instruction_that(
                validate_post_eds=do_return(return_value))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.assert_phase_instruction_that(validate_post_eds=do_raise(exception))


def instruction_validation_invocations() -> list:
    return [
        SetupConfig(),
        ActConfig(),
        BeforeAssertConfig(),
        AssertConfig(),
    ]


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTests(utils.suite_for(conf)
                     for conf in instruction_validation_invocations())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
