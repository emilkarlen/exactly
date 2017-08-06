import unittest

from exactly_lib.execution.phase_step_identifiers import phase_step_simple as step
from exactly_lib.execution.phase_step_identifiers.phase_step import SimplePhaseStep
from exactly_lib.symbol.symbol_usage import SymbolDefinition
from exactly_lib.test_case.phase_identifier import PhaseEnum
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.execution.partial_execution.test_resources.basic import Arrangement, test__va
from exactly_lib_test.execution.test_resources.execution_recording import phase_step_recordings as psr
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that
from exactly_lib_test.execution.test_resources.test_case_generation import partial_test_case_with_instructions
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.test_resources.functions import Sequence
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestPropagationOfSymbolBetweenPhases),
        unittest.makeSuite(TestPropagationOfSymbolsPredefinedInConfiguration),
    ])


class TestPropagationOfSymbolBetweenPhases(unittest.TestCase):
    def test_symbol_table_should_be_empty_when_no_symbols_are_defined(self):
        expected_phase_2_step_2_names_set = {
            PhaseEnum.SETUP: psr.same_value_for_all_steps(step.ALL_SETUP_WITH_ENV_ARG, frozenset()),
            PhaseEnum.ACT: psr.same_value_for_all_steps(step.ALL_ACT_WITH_ENV_ARG, frozenset()),
            PhaseEnum.BEFORE_ASSERT: psr.same_value_for_all_steps(step.ALL_BEFORE_ASSERT_WITH_ENV_ARG, frozenset()),
            PhaseEnum.ASSERT: psr.same_value_for_all_steps(step.ALL_ASSERT_WITH_ENV_ARG, frozenset()),
            PhaseEnum.CLEANUP: psr.same_value_for_all_steps(step.ALL_CLEANUP_WITH_ENV_ARG, frozenset()),
        }
        actual_phase_2_step_2_names_set = psr.new_phase_enum_2_empty_dict()

        def recorder_for(phase_step: SimplePhaseStep):
            return psr.StepRecordingAction(phase_step,
                                           actual_phase_2_step_2_names_set,
                                           get_symbols_name_set_from_instruction_environment)

        test_case = partial_test_case_with_instructions(
            [
                psr.setup_phase_instruction_that_records_a_value_per_step(recorder_for)
            ],
            psr.act_phase_instructions_that_does_nothing(),
            [
                psr.before_assert_phase_instruction_that_records_a_value_per_step(recorder_for)
            ],
            [
                psr.assert_phase_instruction_that_records_a_value_per_step(recorder_for)
            ],
            [
                psr.cleanup_phase_instruction_that_records_a_value_per_step(recorder_for)
            ],
        )
        test__va(
            self,
            test_case,
            Arrangement(psr.act_phase_handling_that_records__a_value_per_step(recorder_for)),
            asrt.anything_goes())
        _check_result(self,
                      expected_phase_2_step_2_names_set,
                      actual_phase_2_step_2_names_set)

    def test_one_symbol_is_defined_in_the_setup_phase(self):
        symbol_name = 'symbol_name'
        all_defined_symbols = frozenset((symbol_name,))
        symbol_definition = symbol_utils.string_symbol_definition(symbol_name, 'symbol value (not used in test)')
        symbol_usages_of_instruction_that_defines_symbol = [symbol_definition]

        steps_for_act = psr.same_value_for_all_steps(step.ALL_ACT_AFTER_PARSE, all_defined_symbols)
        steps_for_act[step.ACT__PARSE.step] = frozenset()

        expected_phase_2_step_2_names_set = {
            PhaseEnum.SETUP: {
                step.SETUP__VALIDATE_PRE_SDS.step: all_defined_symbols,
                step.SETUP__MAIN.step: frozenset(),
                step.SETUP__VALIDATE_POST_SETUP.step: all_defined_symbols,
            },
            PhaseEnum.ACT: steps_for_act,
            PhaseEnum.BEFORE_ASSERT: psr.same_value_for_all_steps(step.ALL_BEFORE_ASSERT_WITH_ENV_ARG,
                                                                  all_defined_symbols),
            PhaseEnum.ASSERT: psr.same_value_for_all_steps(step.ALL_ASSERT_WITH_ENV_ARG, all_defined_symbols),
            PhaseEnum.CLEANUP: psr.same_value_for_all_steps(step.ALL_CLEANUP_WITH_ENV_ARG, all_defined_symbols),
        }
        actual_phase_2_step_2_names_set = psr.new_phase_enum_2_empty_dict()

        def recorder_for(phase_step: SimplePhaseStep):
            return psr.StepRecordingAction(phase_step,
                                           actual_phase_2_step_2_names_set,
                                           get_symbols_name_set_from_instruction_environment)

        test_case = partial_test_case_with_instructions(
            [
                setup_phase_instruction_that(
                    symbol_usages=do_return(symbol_usages_of_instruction_that_defines_symbol),
                    validate_pre_sds_initial_action=recorder_for(step.SETUP__VALIDATE_PRE_SDS),
                    main_initial_action=Sequence([
                        recorder_for(step.SETUP__MAIN),
                        _ActionThatSetsSymbolInSymbolTable(symbol_definition),
                    ]),
                    validate_post_setup_initial_action=recorder_for(step.SETUP__VALIDATE_POST_SETUP),
                )
            ],
            psr.act_phase_instructions_that_does_nothing(),
            [
                psr.before_assert_phase_instruction_that_records_a_value_per_step(recorder_for)
            ],
            [
                psr.assert_phase_instruction_that_records_a_value_per_step(recorder_for)
            ],
            [
                psr.cleanup_phase_instruction_that_records_a_value_per_step(recorder_for)
            ],
        )
        test__va(
            self,
            test_case,
            Arrangement(psr.act_phase_handling_that_records__a_value_per_step(recorder_for)),
            asrt.anything_goes())
        _check_result(self,
                      expected_phase_2_step_2_names_set,
                      actual_phase_2_step_2_names_set)


class TestPropagationOfSymbolsPredefinedInConfiguration(unittest.TestCase):
    def test_one_symbol_is_predefined(self):
        predefined_symbol = NameAndValue('predefined symbol name',
                                         'predefined string constant symbol value')

        expected_predefined_symbols = SymbolTable({
            predefined_symbol.name: symbol_utils.string_constant(predefined_symbol.value)
        })
        all_predefined_symbols = frozenset((predefined_symbol.name,))

        expected_phase_2_step_2_names_set = {
            PhaseEnum.SETUP: psr.same_value_for_all_steps(step.ALL_SETUP_WITH_ENV_ARG, all_predefined_symbols),
            PhaseEnum.ACT: psr.same_value_for_all_steps(step.ALL_ACT_WITH_ENV_ARG, all_predefined_symbols),
            PhaseEnum.BEFORE_ASSERT: psr.same_value_for_all_steps(step.ALL_BEFORE_ASSERT_WITH_ENV_ARG,
                                                                  all_predefined_symbols),
            PhaseEnum.ASSERT: psr.same_value_for_all_steps(step.ALL_ASSERT_WITH_ENV_ARG, all_predefined_symbols),
            PhaseEnum.CLEANUP: psr.same_value_for_all_steps(step.ALL_CLEANUP_WITH_ENV_ARG, all_predefined_symbols),
        }
        actual_phase_2_step_2_names_set = psr.new_phase_enum_2_empty_dict()

        def recorder_for(phase_step: SimplePhaseStep):
            return psr.StepRecordingAction(phase_step,
                                           actual_phase_2_step_2_names_set,
                                           get_symbols_name_set_from_instruction_environment)

        test_case = partial_test_case_with_instructions(
            [
                psr.setup_phase_instruction_that_records_a_value_per_step(recorder_for)
            ],
            psr.act_phase_instructions_that_does_nothing(),
            [
                psr.before_assert_phase_instruction_that_records_a_value_per_step(recorder_for)
            ],
            [
                psr.assert_phase_instruction_that_records_a_value_per_step(recorder_for)
            ],
            [
                psr.cleanup_phase_instruction_that_records_a_value_per_step(recorder_for)
            ],
        )
        test__va(
            self,
            test_case,
            Arrangement(psr.act_phase_handling_that_records__a_value_per_step(recorder_for),
                        predefined_symbols=expected_predefined_symbols),
            asrt.anything_goes())
        _check_result(self,
                      expected_phase_2_step_2_names_set,
                      actual_phase_2_step_2_names_set)


def _check_result(put: unittest.TestCase,
                  expected_phase_2_step_2_recorded_value: dict,
                  actual_phase_2_step_2_recorded_value: dict):
    assertion = psr.Phase2step2recordedValueAssertion(expected_phase_2_step_2_recorded_value)
    assertion.apply_with_message(put,
                                 actual_phase_2_step_2_recorded_value,
                                 'recorded values')


def get_symbols_name_set_from_instruction_environment(environment: InstructionEnvironmentForPreSdsStep,
                                                      *args, **kwargs):
    return environment.symbols.names_set


class _ActionThatSetsSymbolInSymbolTable:
    def __init__(self, symbol: SymbolDefinition):
        self.symbol = symbol

    def __call__(self, environment: InstructionEnvironmentForPreSdsStep, *args, **kwargs):
        environment.symbols.put(self.symbol.name,
                                self.symbol.resolver_container)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
