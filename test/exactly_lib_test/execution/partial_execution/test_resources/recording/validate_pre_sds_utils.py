import unittest

from exactly_lib.execution.partial_execution.result import PartialResultStatus
from exactly_lib.execution.phase_step import PhaseStep
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.test_case.result import svh
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, execute_test_case_with_recording
from exactly_lib_test.execution.partial_execution.test_resources.test_case_generator import PartialPhase
from exactly_lib_test.execution.test_resources import instruction_test_resources as test
from exactly_lib_test.execution.test_resources.result_assertions import \
    action_to_check_has_not_executed_completely
from exactly_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForInstructionFailure


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


class TestCaseBase(unittest.TestCase):
    def __init__(self, configuration: Configuration):
        super().__init__()
        self.configuration = configuration

    def shortDescription(self):
        return str(type(self)) + ': ' + str(type(self.configuration))


class TestValidationError(TestCaseBase):
    def runTest(self):
        conf = self.configuration
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(conf.phase,
                 conf.instruction_that_returns(svh.new_svh_validation_error('validation error message')))
        execute_test_case_with_recording(
            self,
            Arrangement(test_case),
            Expectation(PartialResultStatus.VALIDATION_ERROR,
                        action_to_check_has_not_executed_completely(),
                        ExpectedFailureForInstructionFailure.new_with_message(
                            conf.step,
                            test_case.the_extra(conf.phase)[0].source,
                            'validation error message'),
                        conf.expected_steps,
                        False)
        )


class TestHardError(TestCaseBase):
    def runTest(self):
        conf = self.configuration
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(conf.phase,
                 conf.instruction_that_returns(svh.new_svh_hard_error('Error message from hard error')))
        execute_test_case_with_recording(
            self,
            Arrangement(test_case),
            Expectation(PartialResultStatus.HARD_ERROR,
                        action_to_check_has_not_executed_completely(),
                        ExpectedFailureForInstructionFailure.new_with_message(
                            conf.step,
                            test_case.the_extra(conf.phase)[0].source,
                            'Error message from hard error'),
                        conf.expected_steps,
                        False))


class TestImplementationError(TestCaseBase):
    def runTest(self):
        conf = self.configuration
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(conf.phase,
                 conf.instruction_that_raises(test.ImplementationErrorTestException()))
        execute_test_case_with_recording(
            self,
            Arrangement(test_case),
            Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                        action_to_check_has_not_executed_completely(),
                        ExpectedFailureForInstructionFailure.new_with_exception(
                            conf.step,
                            test_case.the_extra(conf.phase)[0].source,
                            test.ImplementationErrorTestException),
                        conf.expected_steps,
                        False))


def suite_for(configuration: Configuration) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTests([TestValidationError(configuration),
                      TestHardError(configuration),
                      TestImplementationError(configuration),
                      ])
    return ret_val
