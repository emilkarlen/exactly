import unittest

from shellcheck_lib.execution import phase_step
from shellcheck_lib.execution.result import PartialResultStatus
from shellcheck_lib_test.execution.partial_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase, one_successful_instruction_in_each_phase
from shellcheck_lib_test.execution.test_resources.execution_recording.phase_steps import PRE_EDS_VALIDATION_STEPS
from shellcheck_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForNoFailure


class Test(TestCaseBase):
    def test_full_sequence(self):
        self._check(
                Arrangement(one_successful_instruction_in_each_phase()),
                Expectation(PartialResultStatus.PASS,
                            ExpectedFailureForNoFailure(),
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.SETUP_VALIDATE_POST_SETUP,
                             phase_step.ACT_VALIDATE_POST_SETUP,
                             phase_step.BEFORE_ASSERT_VALIDATE_POST_SETUP,
                             phase_step.ASSERT_VALIDATE_POST_EDS,
                             phase_step.ACT_MAIN,
                             phase_step.ACT_SCRIPT_VALIDATE,
                             phase_step.ACT_SCRIPT_EXECUTE,
                             phase_step.BEFORE_ASSERT_MAIN,
                             phase_step.ASSERT_MAIN,
                             phase_step.CLEANUP_MAIN,
                             ],
                            True))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
