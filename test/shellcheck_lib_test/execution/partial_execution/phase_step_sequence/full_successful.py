import unittest

from shellcheck_lib.execution import phase_step
from shellcheck_lib.execution.result import PartialResultStatus
from shellcheck_lib_test.execution.partial_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase, one_successful_instruction_in_each_phase
from shellcheck_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForNoFailure


class Test(TestCaseBase):
    def test_full_sequence(self):
        self._check(
                Arrangement(one_successful_instruction_in_each_phase()),
                Expectation(PartialResultStatus.PASS,
                            ExpectedFailureForNoFailure(),
                            [phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__MAIN,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.ACT__VALIDATE,
                             phase_step.ASSERT__VALIDATE,
                             phase_step.ACT__SCRIPT_GENERATE,
                             phase_step.ACT__SCRIPT_VALIDATE,
                             phase_step.ACT__SCRIPT_EXECUTE,
                             phase_step.ASSERT__MAIN,
                             phase_step.CLEANUP,
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
