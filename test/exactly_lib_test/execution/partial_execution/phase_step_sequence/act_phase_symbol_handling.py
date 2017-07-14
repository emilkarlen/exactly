import unittest

from exactly_lib.execution.phase_step_identifiers import phase_step_simple as phase_step
from exactly_lib.execution.result import PartialResultStatus
from exactly_lib.symbol.restrictions.value_restrictions import StringRestriction
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList, \
    TestCaseGeneratorForExecutionRecording
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase
from exactly_lib_test.execution.test_resources import instruction_test_resources as test
from exactly_lib_test.execution.test_resources.execution_recording.phase_steps import SYMBOL_VALIDATION_STEPS__ONCE, \
    PRE_SDS_VALIDATION_STEPS__ONCE
from exactly_lib_test.execution.test_resources.test_actions import action_that_returns, action_that_raises
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.symbol_utils import symbol_reference
from exactly_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForPhaseFailure, \
    ExpectedFailureForNoFailure


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulScenarios),
        unittest.makeSuite(TestFailingScenarios),
    ])


class TestSuccessfulScenarios(TestCaseBase):
    def test_symbol_that_does_meet_restriction_in_validate_symbols(self):
        test_case = _single_successful_instruction_in_each_phase()
        symbol_name = 'symbol_name'
        reference_to_string_symbol = symbol_utils.symbol_reference(symbol_name,
                                                                   StringRestriction())
        definition_of_string_symbol = symbol_utils.string_symbol_definition(symbol_name)
        symbol_usages = [
            definition_of_string_symbol,
            reference_to_string_symbol,
        ]
        self._check(
            Arrangement(test_case,
                        act_executor_symbol_usages=action_that_returns(symbol_usages)),
            Expectation(PartialResultStatus.PASS,
                        ExpectedFailureForNoFailure(),
                        SYMBOL_VALIDATION_STEPS__ONCE +

                        PRE_SDS_VALIDATION_STEPS__ONCE +

                        [phase_step.SETUP__MAIN,

                         phase_step.SETUP__VALIDATE_POST_SETUP,
                         phase_step.ACT__VALIDATE_POST_SETUP,
                         phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                         phase_step.ASSERT__VALIDATE_POST_SETUP,

                         phase_step.ACT__PREPARE,
                         phase_step.ACT__EXECUTE,

                         phase_step.BEFORE_ASSERT__MAIN,
                         phase_step.ASSERT__MAIN,
                         (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                         ],
                        sandbox_directory_structure_should_exist=True))


class TestFailingScenarios(TestCaseBase):
    def test_reference_to_undefined_symbol_in_validate_symbols(self):
        test_case = _single_successful_instruction_in_each_phase()
        symbol_usages_with_ref_to_undefined_symbol = [symbol_reference('undefined_symbol')]
        self._check(
            Arrangement(test_case,
                        act_executor_symbol_usages=action_that_returns(symbol_usages_with_ref_to_undefined_symbol)),
            Expectation(PartialResultStatus.VALIDATE,
                        ExpectedFailureForPhaseFailure.new_with_step(phase_step.ACT__VALIDATE_SYMBOLS),
                        [
                            phase_step.SETUP__VALIDATE_SYMBOLS,
                            phase_step.ACT__VALIDATE_SYMBOLS,
                        ],
                        sandbox_directory_structure_should_exist=False))

    def test_implementation_error_in_validate_symbols(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case,
                        act_executor_symbol_usages=action_that_raises(test.ImplementationErrorTestException())),
            Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                        ExpectedFailureForPhaseFailure.new_with_step(phase_step.ACT__VALIDATE_SYMBOLS),
                        [
                            phase_step.SETUP__VALIDATE_SYMBOLS,
                            phase_step.ACT__VALIDATE_SYMBOLS,
                        ],
                        sandbox_directory_structure_should_exist=False))

    def test_symbol_that_does_not_meet_restriction_in_validate_symbols(self):
        test_case = _single_successful_instruction_in_each_phase()
        symbol_name = 'symbol_name'
        reference_to_string_symbol = symbol_utils.symbol_reference(symbol_name,
                                                                   StringRestriction())
        definition_of_path_symbol = symbol_utils.file_ref_symbol_definition(symbol_name)
        symbol_usages = [
            definition_of_path_symbol,
            reference_to_string_symbol,
        ]
        self._check(
            Arrangement(test_case,
                        act_executor_symbol_usages=action_that_returns(symbol_usages)),
            Expectation(PartialResultStatus.VALIDATE,
                        ExpectedFailureForPhaseFailure.new_with_step(phase_step.ACT__VALIDATE_SYMBOLS),
                        [
                            phase_step.SETUP__VALIDATE_SYMBOLS,
                            phase_step.ACT__VALIDATE_SYMBOLS,
                        ],
                        sandbox_directory_structure_should_exist=False))


def _single_successful_instruction_in_each_phase() -> TestCaseGeneratorForExecutionRecording:
    return TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
