import unittest

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.execution import phase_step
from exactly_lib.impls.actors.util.actor_from_parts import parts as sut
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case.actor import ParseException
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep
from exactly_lib.type_val_deps.sym_ref.data.reference_restrictions import is_any_data_type
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.impls.actors.test_resources.integration_check import Arrangement, simple_success, \
    check_execution, Expectation
from exactly_lib_test.impls.actors.util.actor_from_parts.test_resources import ParserThatRaisesException, \
    ParserThatExpectsSingleInstructionAndRecordsAndReturnsTheTextOfThatInstruction, \
    SymbolUserWithConstantSymbolReferences, ParserWithConstantResult, ValidatorConstructorThatRaises, \
    ExecutorConstructorThatRaises, ValidatorConstructorThatRecordsStep, ExecutorConstructorThatRecordsStep, \
    _ExecutorConstructorForConstant, UnconditionallySuccessfulExecutor, ExecutorThat
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPreSdsBuilder
from exactly_lib_test.test_resources.actions import do_raise
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.data.test_resources import concrete_restriction_assertion


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestConstructor))
    return ret_val


class TestConstructor(unittest.TestCase):
    def test_WHEN_parser_raises_exception_THEN_parse_SHOULD_raise_this_exception(self):
        # ARRANGE #
        parser_error = text_docs.single_pre_formatted_line_object('msg')
        actor = sut.ActorFromParts(ParserThatRaisesException(parser_error),
                                   ValidatorConstructorThatRaises(),
                                   ExecutorConstructorThatRaises())
        act_phase_instructions = []
        # ACT #
        with self.assertRaises(ParseException) as ex:
            executor = actor.parse(act_phase_instructions)
            # ASSERT #
            self.assertIs(parser_error, ex)

    def test_symbol_usages_of_object_returned_by_parser_SHOULD_be_reported(self):
        # ARRANGE #
        symbol_reference = NameAndValue('symbol_name',
                                        is_any_data_type())
        expected_symbol_references = [
            SymbolReference(symbol_reference.name,
                            symbol_reference.value)
        ]
        actor = sut.ActorFromParts(
            ParserWithConstantResult(
                SymbolUserWithConstantSymbolReferences(expected_symbol_references)
            ),
            sut.UnconditionallySuccessfulValidatorConstructor(),
            _ExecutorConstructorForConstant(UnconditionallySuccessfulExecutor()),
        )
        # ACT & ASSERT #
        check_execution(self,
                        actor,
                        [],
                        Arrangement(),
                        Expectation(
                            symbol_usages=asrt.matches_sequence([
                                asrt_sym_ref.matches_reference_2(
                                    symbol_reference.name,
                                    concrete_restriction_assertion.equals_data_type_reference_restrictions(
                                        symbol_reference.value)
                                )
                            ])
                        ))

    def test_full_sequence_of_steps(self):
        # ARRANGE #
        step_recorder = dict()
        actor = ParserThatExpectsSingleInstructionAndRecordsAndReturnsTheTextOfThatInstruction(step_recorder)

        actor = sut.ActorFromParts(actor,
                                   ValidatorConstructorThatRecordsStep(step_recorder),
                                   ExecutorConstructorThatRecordsStep(step_recorder))
        act_phase_instructions = [instr(['act phase source'])]
        arrangement = Arrangement()
        expectation = simple_success()
        # ACT #
        check_execution(self,
                        actor,
                        act_phase_instructions,
                        arrangement,
                        expectation)
        # ASSERT #
        expected_recordings = {
            phase_step.ACT__PARSE: 'act phase source',
            phase_step.ACT__VALIDATE_PRE_SDS: 'act phase source',
            phase_step.ACT__VALIDATE_POST_SETUP: 'act phase source',
            phase_step.ACT__PREPARE: 'act phase source',
            phase_step.ACT__EXECUTE: 'act phase source',
        }
        self.assertDictEqual(expected_recordings,
                             step_recorder)

    def test_hard_error_exception_from_executor_prepare_SHOULD_be_handled(self):
        # ARRANGE #
        act_phase_instructions = []
        hard_error_message = 'the err msg'

        actor = sut.ActorFromParts(
            ParserWithConstantResult(
                SymbolUserWithConstantSymbolReferences(())
            ),
            sut.UnconditionallySuccessfulValidatorConstructor(),
            _ExecutorConstructorForConstant(
                ExecutorThat(
                    prepare=
                    do_raise(HardErrorException(
                        asrt_text_doc.new_single_string_text_for_test(hard_error_message)
                    ))
                )
            ),
        )

        arrangement = Arrangement()
        expectation = Expectation.hard_error_from_prepare(
            error_message=asrt_text_doc.is_single_pre_formatted_text_that_equals(hard_error_message)
        )
        # ACT & ASSERT #
        check_execution(self,
                        actor,
                        act_phase_instructions,
                        arrangement,
                        expectation)

    def test_hard_error_exception_from_executor_execute_SHOULD_be_handled(self):
        # ARRANGE #
        act_phase_instructions = []
        hard_error_message = 'the err msg'

        actor = sut.ActorFromParts(
            ParserWithConstantResult(
                SymbolUserWithConstantSymbolReferences(())
            ),
            sut.UnconditionallySuccessfulValidatorConstructor(),
            _ExecutorConstructorForConstant(
                ExecutorThat(
                    execute_initial_action=
                    do_raise(HardErrorException(
                        asrt_text_doc.new_single_string_text_for_test(hard_error_message)
                    ))
                )
            ),
        )

        arrangement = Arrangement()
        expectation = Expectation.hard_error_from_execute(
            error_message=asrt_text_doc.is_single_pre_formatted_text_that_equals(hard_error_message)
        )
        # ACT & ASSERT #
        check_execution(self,
                        actor,
                        act_phase_instructions,
                        arrangement,
                        expectation)


def _environment() -> InstructionEnvironmentForPreSdsStep:
    return InstructionEnvironmentPreSdsBuilder.of_empty_env().build
