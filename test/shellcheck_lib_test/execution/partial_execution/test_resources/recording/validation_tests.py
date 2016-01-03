import unittest

from shellcheck_lib.execution import phase_step
from shellcheck_lib.execution.phase_step import PhaseStep
from shellcheck_lib.execution.result import PartialResultStatus
from shellcheck_lib.test_case.sections.common import TestCaseInstruction
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.execution.partial_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase, one_successful_instruction_in_each_phase, execute_test_case_with_recording
from shellcheck_lib_test.execution.partial_execution.test_resources.test_case_generator import PartialPhase
from shellcheck_lib_test.execution.test_resources import instruction_test_resources as test
from shellcheck_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForInstructionFailure


class Configuration:
    def __init__(self,
                 phase: PartialPhase,
                 step: PhaseStep,
                 expected_steps: list):
        super().__init__()
        self.phase = phase
        self.step = step
        self.expected_steps = expected_steps

    def instruction_that_returns(self, return_value: svh.SuccessOrValidationErrorOrHardError) -> TestCaseInstruction:
        raise NotImplementedError()

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        raise NotImplementedError()


class TestValidationError(unittest.TestCase):
    def __init__(self, configuration: Configuration):
        super(TestValidationError, self).__init__()
        self.configuration = configuration

    def runTest(self):
        conf = self.configuration
        test_case = one_successful_instruction_in_each_phase() \
            .add(conf.phase,
                 conf.instruction_that_returns(svh.new_svh_validation_error('validation error message')))
        execute_test_case_with_recording(
                self,
                Arrangement(test_case),
                Expectation(PartialResultStatus.VALIDATE,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    conf.step,
                                    test_case.the_extra(conf.phase)[0].first_line,
                                    'validation error message'),
                            conf.expected_steps,
                            False)
        )


class TestHardError(unittest.TestCase):
    def __init__(self, configuration: Configuration):
        super().__init__()
        self.configuration = configuration

    def runTest(self):
        conf = self.configuration
        test_case = one_successful_instruction_in_each_phase() \
            .add(conf.phase,
                 conf.instruction_that_returns(svh.new_svh_hard_error('Error message from hard error')))
        execute_test_case_with_recording(
                self,
                Arrangement(test_case),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    conf.step,
                                    test_case.the_extra(conf.phase)[0].first_line,
                                    'Error message from hard error'),
                            conf.expected_steps,
                            False))


class TestImplementationError(unittest.TestCase):
    def __init__(self, configuration: Configuration):
        super().__init__()
        self.configuration = configuration

    def runTest(self):
        conf = self.configuration
        test_case = one_successful_instruction_in_each_phase() \
            .add(conf.phase,
                 conf.instruction_that_raises(test.ImplementationErrorTestException))
        execute_test_case_with_recording(
                self,
                Arrangement(test_case),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    conf.step,
                                    test_case.the_extra(conf.phase)[0].first_line,
                                    test.ImplementationErrorTestException),
                            conf.expected_steps,
                            False))


def suite_for(configuration: Configuration) -> list:
    ret_val = unittest.TestSuite()
    ret_val.addTests([TestValidationError(configuration),
                      TestHardError(configuration),
                      TestImplementationError(configuration),
                      ])
    return ret_val


class TestCaseWithValidationTestsBase(TestCaseBase):
    def _check_validate__validation_error(self,
                                          configuration: Configuration):
        test_case = one_successful_instruction_in_each_phase() \
            .add(configuration.phase,
                 configuration.instruction_that_returns(svh.new_svh_validation_error('validation error message')))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.VALIDATE,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    configuration.step,
                                    test_case.the_extra(configuration.phase)[0].first_line,
                                    'validation error message'),
                            configuration.expected_steps,
                            False))

    def _check_validate__hard_error(self,
                                    configuration: Configuration):
        test_case = one_successful_instruction_in_each_phase() \
            .add(configuration.phase,
                 configuration.instruction_that_returns(svh.new_svh_hard_error('Error message from hard error')))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    configuration.step,
                                    test_case.the_extra(configuration.phase)[0].first_line,
                                    'Error message from hard error'),
                            configuration.expected_steps,
                            False))


class Test(TestCaseWithValidationTestsBase):
    def test_validation_error_in_setup_validate_step2(self):
        self._check_validate__validation_error(SetupForSetupValidatePreEds())

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

    def test_hard_error_in_setup_validate_step2(self):
        self._check_validate__hard_error(SetupForSetupValidatePreEds())

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
    ret_val.addTests(suite_for(SetupForSetupValidatePreEds()))
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
