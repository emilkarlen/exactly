import unittest

from shellcheck_lib.execution import phase_step
from shellcheck_lib.execution.result import PartialResultStatus
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.execution.partial_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase, one_successful_instruction_in_each_phase
from shellcheck_lib_test.execution.partial_execution.test_resources.test_case_generator import PartialPhase
from shellcheck_lib_test.execution.test_resources import instruction_test_resources as test
from shellcheck_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForInstructionFailure


class Test(TestCaseBase):
    def test_validation_error_in_setup_validate_step(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.SETUP,
                 test.SetupPhaseInstructionThatReturns(
                         svh.new_svh_validation_error(
                                 'validation error from setup/validate'),
                         sh.new_sh_success(),
                         svh.new_svh_success()))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.VALIDATE,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.SETUP_PRE_VALIDATE,
                                    test_case.the_extra(PartialPhase.SETUP)[0].first_line,
                                    'validation error from setup/validate'),
                            [phase_step.SETUP_PRE_VALIDATE,
                             ],
                            False))

    def test_hard_error_in_setup_validate_step(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.SETUP,
                 test.SetupPhaseInstructionThatReturns(
                         svh.new_svh_hard_error('hard error from setup/validate'),
                         sh.new_sh_success(),
                         svh.new_svh_success()))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.SETUP_PRE_VALIDATE,
                                    test_case.the_extra(PartialPhase.SETUP)[0].first_line,
                                    'hard error from setup/validate'),
                            [phase_step.SETUP_PRE_VALIDATE,
                             ],
                            False))

    def test_implementation_error_in_setup_validate_step(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.SETUP,
                 test.SetupPhaseInstructionWithImplementationErrorInPreValidate(
                         test.ImplementationErrorTestException()))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    phase_step.SETUP_PRE_VALIDATE,
                                    test_case.the_extra(PartialPhase.SETUP)[0].first_line,
                                    test.ImplementationErrorTestException),
                            [phase_step.SETUP_PRE_VALIDATE,
                             ],
                            False))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
