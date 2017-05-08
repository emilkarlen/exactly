import unittest

from exactly_lib.execution.phase_step_identifiers.phase_step import PhaseStep
from exactly_lib.execution.result import PartialResultStatus
from exactly_lib.symbol.concrete_restrictions import NoRestriction
from exactly_lib.symbol.value_structure import SymbolReference
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, execute_test_case_with_recording
from exactly_lib_test.execution.partial_execution.test_resources.test_case_generator import PartialPhase
from exactly_lib_test.execution.test_resources import instruction_test_resources as test
from exactly_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForInstructionFailure
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class Configuration:
    def __init__(self,
                 phase: PartialPhase,
                 step: PhaseStep,
                 expected_steps_before_failing_instruction: list):
        super().__init__()
        self.phase = phase
        self.step = step
        self.expected_steps_before_failing_instruction = expected_steps_before_failing_instruction

    def instruction_that_returns(self, symbol_usages: list) -> TestCaseInstruction:
        raise NotImplementedError()

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        raise NotImplementedError()


def suite_for(configuration: Configuration) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTests([TestValidationError(configuration),
                      TestImplementationError(configuration)
                      ])
    return ret_val


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
                 conf.instruction_that_returns([_reference_to_undefined_symbol()]))
        execute_test_case_with_recording(
            self,
            Arrangement(test_case),
            Expectation(PartialResultStatus.VALIDATE,
                        ExpectedFailureForInstructionFailure.new_with_message_assertion(
                            conf.step,
                            test_case.the_extra(conf.phase)[0].first_line,
                            asrt.is_instance(str)),
                        conf.expected_steps_before_failing_instruction,
                        sandbox_directory_structure_should_exist=False)
        )


class TestImplementationError(TestCaseBase):
    def runTest(self):
        conf = self.configuration
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
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
                        conf.expected_steps_before_failing_instruction,
                        sandbox_directory_structure_should_exist=False))


def _reference_to_undefined_symbol() -> SymbolReference:
    return SymbolReference('undefined symbol', NoRestriction())
