import unittest

from shellcheck_lib.execution import phase_step, phases
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.test_case.sections.anonymous import ExecutionMode
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.execution.full_execution.test_resources import instruction_test_resources
from shellcheck_lib_test.execution.full_execution.test_resources.instruction_test_resources import \
    AnonymousPhaseInstructionThatSetsExecutionMode
from shellcheck_lib_test.execution.full_execution.test_resources.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList
from shellcheck_lib_test.execution.full_execution.test_resources.test_case_that_records_phase_execution import \
    new_test_case_with_recording
from shellcheck_lib_test.util.expected_instruction_failure import ExpectedFailureForInstructionFailure, \
    ExpectedFailureForNoFailure


class Test(unittest.TestCase):
    def test_with_assert_phase_that_fails(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(AnonymousPhaseInstructionThatSetsExecutionMode(ExecutionMode.XFAIL)) \
            .add_assert(
            instruction_test_resources.AssertPhaseInstructionThatReturns(
                from_validate=svh.new_svh_success(),
                from_execute=pfh.new_pfh_fail('fail message')))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.XFAIL,
            ExpectedFailureForInstructionFailure.new_with_message(
                phase_step.PhaseStep(phases.ASSERT, phase_step.EXECUTE),
                test_case.the_assert_phase_extra[0].first_line,
                'fail message'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATE,
             phase_step.ACT__SCRIPT_VALIDATE,
             phase_step.ACT__SCRIPT_EXECUTE,
             phase_step.ASSERT__EXECUTE,
             phase_step.CLEANUP
             ],
            True).execute()

    def test_with_assert_phase_that_passes(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(AnonymousPhaseInstructionThatSetsExecutionMode(ExecutionMode.XFAIL))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.XPASS,
            ExpectedFailureForNoFailure(),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATE,
             phase_step.ACT__SCRIPT_VALIDATE,
             phase_step.ACT__SCRIPT_EXECUTE,
             phase_step.ASSERT__EXECUTE,
             phase_step.CLEANUP
             ],
            True).execute()

    def test_with_anonymous_phase_with_hard_error(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(AnonymousPhaseInstructionThatSetsExecutionMode(ExecutionMode.XFAIL)) \
            .add_anonymous(instruction_test_resources.AnonymousPhaseInstructionThatReturns(
            sh.new_sh_hard_error('hard error msg')))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedFailureForInstructionFailure.new_with_message(
                phase_step.new_without_step(phases.ANONYMOUS),
                test_case.the_anonymous_phase_extra[1].first_line,
                'hard error msg'),
            [phase_step.ANONYMOUS
             ],
            False).execute()

    def test_with_implementation_error(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(AnonymousPhaseInstructionThatSetsExecutionMode(ExecutionMode.XFAIL)) \
            .add_cleanup(
            instruction_test_resources.CleanupPhaseInstructionWithImplementationError(
                instruction_test_resources.ImplementationErrorTestException()))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedFailureForInstructionFailure.new_with_exception(
                phase_step.new_without_step(phases.CLEANUP),
                test_case.the_cleanup_phase_extra[0].first_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATE,
             phase_step.ACT__SCRIPT_VALIDATE,
             phase_step.ACT__SCRIPT_EXECUTE,
             phase_step.ASSERT__EXECUTE,
             phase_step.CLEANUP
             ],
            True).execute()


if __name__ == '__main__':
    unittest.main()
