import unittest

from exactly_lib.execution.partial_execution.result import PartialExeResultStatus
from exactly_lib.execution.phase_step import SimplePhaseStep
from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.data.restrictions.value_restrictions import AnyDataTypeRestriction
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.symbol_usage import SymbolReference, SymbolDefinition
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib_test.execution.partial_execution.test_resources import result_assertions as asrt_result
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, execute_test_case_with_recording
from exactly_lib_test.execution.partial_execution.test_resources.test_case_generator import PartialPhase
from exactly_lib_test.execution.test_resources import instruction_test_resources as test
from exactly_lib_test.execution.test_resources.failure_info_check import ExpectedFailureForInstructionFailure
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    value_restriction_that_is_unconditionally_unsatisfied
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.test_resources.symbol_utils import element_reference
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class Configuration:
    def __init__(self,
                 phase: PartialPhase,
                 step: SimplePhaseStep,
                 expected_steps_before_failing_instruction: list):
        super().__init__()
        self.phase = phase
        self.step = step
        self.expected_steps_before_failing_instruction = expected_steps_before_failing_instruction

    def instruction_that_returns(self, symbol_usages: list) -> TestCaseInstruction:
        raise NotImplementedError()

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        raise NotImplementedError()

    @property
    def phase_is_after_act(self) -> bool:
        return self.phase > PartialPhase.ACT


def suite_for(configuration: Configuration) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTests([TestValidationErrorDueToReferenceToUndefinedSymbol(configuration),
                      TestValidationErrorDueToFailedReferenceRestrictions(configuration),
                      TestImplementationError(configuration),
                      ])
    return ret_val


class TestCaseBase(unittest.TestCase):
    def __init__(self, configuration: Configuration):
        super().__init__()
        self.configuration = configuration

    def shortDescription(self):
        return str(type(self)) + ': ' + str(type(self.configuration))


class TestValidationErrorDueToReferenceToUndefinedSymbol(TestCaseBase):
    def runTest(self):
        conf = self.configuration
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(conf.phase,
                 conf.instruction_that_returns([element_reference('undefined symbol')]))
        execute_test_case_with_recording(
            self,
            Arrangement(test_case),
            Expectation(
                asrt_result.matches2(
                    PartialExeResultStatus.VALIDATION_ERROR,
                    asrt_result.has_no_sds(),
                    asrt_result.has_no_action_to_check_outcome(),
                    ExpectedFailureForInstructionFailure.new_with_message_assertion(
                        conf.step,
                        test_case.the_extra(conf.phase)[0].source,
                        asrt.is_instance(str)),
                ),
                conf.expected_steps_before_failing_instruction,
            )
        )


class TestValidationErrorDueToFailedReferenceRestrictions(TestCaseBase):
    def runTest(self):
        conf = self.configuration
        defined_symbol = data_symbol_utils.string_symbol_definition('symbol_name')
        error_message_for_failed_restriction = 'error message'
        reference_with_restriction_failure = SymbolReference(
            defined_symbol.name,
            ReferenceRestrictionsOnDirectAndIndirect(
                direct=value_restriction_that_is_unconditionally_unsatisfied(error_message_for_failed_restriction)))

        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.SETUP,
                 setup_phase_instruction_that(symbol_usages=do_return([defined_symbol]))) \
            .add(conf.phase,
                 conf.instruction_that_returns([reference_with_restriction_failure]))

        execute_test_case_with_recording(
            self,
            Arrangement(test_case),
            Expectation(
                asrt_result.matches2(
                    PartialExeResultStatus.VALIDATION_ERROR,
                    asrt_result.has_no_sds(),
                    asrt_result.has_no_action_to_check_outcome(),
                    ExpectedFailureForInstructionFailure.new_with_phase_and_message_assertion(
                        conf.step,
                        asrt.equals(error_message_for_failed_restriction)),
                ),
                conf.expected_steps_before_failing_instruction,
            )
        )


class TestImplementationError(TestCaseBase):
    def runTest(self):
        conf = self.configuration
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(conf.phase,
                 conf.instruction_that_raises(test.ImplementationErrorTestException()))
        execute_test_case_with_recording(
            self,
            Arrangement(test_case),
            Expectation(
                asrt_result.matches2(
                    PartialExeResultStatus.IMPLEMENTATION_ERROR,
                    asrt_result.has_no_sds(),
                    asrt_result.has_no_action_to_check_outcome(),
                    ExpectedFailureForInstructionFailure.new_with_exception(
                        conf.step,
                        test_case.the_extra(conf.phase)[0].source,
                        test.ImplementationErrorTestException),
                ),
                conf.expected_steps_before_failing_instruction,
            ))


def _reference_to_undefined_symbol() -> SymbolReference:
    return SymbolReference('undefined symbol',
                           ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction()))


def definition_with_reference(name_of_defined: str,
                              name_of_referenced: str) -> SymbolDefinition:
    symbol_reference = SymbolReference(name_of_referenced,
                                       ReferenceRestrictionsOnDirectAndIndirect(direct=AnyDataTypeRestriction(),
                                                                                indirect=AnyDataTypeRestriction()))
    return SymbolDefinition(name_of_defined,
                            data_symbol_utils.container(
                                StringResolver((string_resolvers.symbol_fragment(symbol_reference),))
                            ))
