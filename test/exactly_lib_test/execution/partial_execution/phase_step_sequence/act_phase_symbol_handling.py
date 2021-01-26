import unittest

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.execution.result import ExecutionFailureStatus
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib.type_val_deps.sym_ref.data.value_restrictions import StringRestriction
from exactly_lib_test.execution.partial_execution.test_resources import result_assertions as asrt_result
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList, \
    TestCaseGeneratorForExecutionRecording
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase
from exactly_lib_test.execution.test_resources import instruction_test_resources as test
from exactly_lib_test.execution.test_resources.execution_recording.phase_steps import SYMBOL_VALIDATION_STEPS__ONCE, \
    PRE_SDS_VALIDATION_STEPS__ONCE
from exactly_lib_test.execution.test_resources.failure_info_check import ExpectedFailureForNoFailure, \
    ExpectedFailureForPhaseFailure
from exactly_lib_test.test_case.actor.test_resources.test_actions import \
    execute_action_that_returns_exit_code
from exactly_lib_test.test_resources.actions import do_return, do_raise
from exactly_lib_test.type_val_deps.data.test_resources import data_symbol_utils
from exactly_lib_test.type_val_deps.data.test_resources.data_symbol_utils import symbol_reference
from exactly_lib_test.type_val_deps.types.path.test_resources.path import arbitrary_path_symbol_context
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulScenarios),
        unittest.makeSuite(TestFailingScenarios),
    ])


class TestSuccessfulScenarios(TestCaseBase):
    def test_symbol_that_does_meet_restriction_in_validate_symbols(self):
        test_case = _single_successful_instruction_in_each_phase()
        symbol_name = 'symbol_name'
        reference_to_string_symbol = data_symbol_utils.symbol_reference(symbol_name,
                                                                        StringRestriction())
        definition_of_string_symbol = StringConstantSymbolContext(symbol_name).definition
        symbol_usages = [
            definition_of_string_symbol,
            reference_to_string_symbol,
        ]
        self._check(
            Arrangement(test_case,
                        atc_symbol_usages=do_return(symbol_usages),
                        atc_execute=execute_action_that_returns_exit_code(128)),
            Expectation(
                asrt_result.matches2(
                    None,
                    asrt_result.has_sds(),
                    asrt_result.has_action_to_check_outcome_with_exit_code(128),
                    ExpectedFailureForNoFailure(),
                ),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__ONCE +

                PRE_SDS_VALIDATION_STEPS__ONCE +

                [phase_step.SETUP__MAIN,

                 phase_step.SETUP__VALIDATE_POST_SETUP,
                 phase_step.ACT__VALIDATE_POST_SETUP,
                 phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                 phase_step.ASSERT__VALIDATE_POST_SETUP,

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 phase_step.ACT__PREPARE,
                 phase_step.ACT__EXECUTE,

                 phase_step.BEFORE_ASSERT__MAIN,
                 phase_step.ASSERT__MAIN,
                 (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                 ],
            ))


class TestFailingScenarios(TestCaseBase):
    def test_reference_to_undefined_symbol_in_validate_symbols(self):
        test_case = _single_successful_instruction_in_each_phase()
        symbol_usages_with_ref_to_undefined_symbol = [symbol_reference('undefined_symbol')]
        self._check(
            Arrangement(test_case,
                        atc_symbol_usages=do_return(symbol_usages_with_ref_to_undefined_symbol)),
            Expectation(
                asrt_result.matches2(
                    ExecutionFailureStatus.VALIDATION_ERROR,
                    asrt_result.has_no_sds(),
                    asrt_result.has_no_action_to_check_outcome(),
                    ExpectedFailureForPhaseFailure.new_with_step(phase_step.ACT__VALIDATE_SYMBOLS),
                ),
                [
                    phase_step.ACT__PARSE,
                    phase_step.SETUP__VALIDATE_SYMBOLS,
                    phase_step.ACT__VALIDATE_SYMBOLS,
                ],
            ))

    def test_internal_error_in_validate_symbols(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case,
                        atc_symbol_usages=do_raise(test.ImplementationErrorTestException())),
            Expectation(
                asrt_result.matches2(ExecutionFailureStatus.INTERNAL_ERROR,
                                     asrt_result.has_no_sds(),
                                     asrt_result.has_no_action_to_check_outcome(),
                                     ExpectedFailureForPhaseFailure.new_with_exception(
                                         phase_step.ACT__VALIDATE_SYMBOLS,
                                         test.ImplementationErrorTestException)
                                     ),
                [
                    phase_step.ACT__PARSE,
                    phase_step.SETUP__VALIDATE_SYMBOLS,
                    phase_step.ACT__VALIDATE_SYMBOLS,
                ],
            ))

    def test_symbol_that_does_not_meet_restriction_in_validate_symbols(self):
        test_case = _single_successful_instruction_in_each_phase()
        symbol_name = 'symbol_name'
        reference_to_string_symbol = data_symbol_utils.symbol_reference(symbol_name,
                                                                        StringRestriction())
        definition_of_path_symbol = arbitrary_path_symbol_context(symbol_name).definition
        symbol_usages = [
            definition_of_path_symbol,
            reference_to_string_symbol,
        ]
        self._check(
            Arrangement(test_case,
                        atc_symbol_usages=do_return(symbol_usages)),
            Expectation(
                asrt_result.matches2(
                    ExecutionFailureStatus.VALIDATION_ERROR,
                    asrt_result.has_no_sds(),
                    asrt_result.has_no_action_to_check_outcome(),
                    ExpectedFailureForPhaseFailure.new_with_step(phase_step.ACT__VALIDATE_SYMBOLS),
                ),
                [
                    phase_step.ACT__PARSE,
                    phase_step.SETUP__VALIDATE_SYMBOLS,
                    phase_step.ACT__VALIDATE_SYMBOLS,
                ],
            ))


def _single_successful_instruction_in_each_phase() -> TestCaseGeneratorForExecutionRecording:
    return TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
