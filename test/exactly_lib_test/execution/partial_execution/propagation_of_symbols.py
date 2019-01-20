import unittest

from exactly_lib.execution import phase_step_simple as step
from exactly_lib.execution.phase_step import SimplePhaseStep
from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.symbol_usage import SymbolDefinition
from exactly_lib.test_case.phase_identifier import PhaseEnum
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.execution.partial_execution.test_resources.basic import Arrangement, test__va
from exactly_lib_test.execution.test_resources.execution_recording import phase_step_recordings as psr
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that, \
    before_assert_phase_instruction_that, assert_phase_instruction_that, cleanup_phase_instruction_that
from exactly_lib_test.execution.test_resources.test_case_generation import partial_test_case_with_instructions
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
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
            PhaseEnum.SETUP: psr.same_value_for_all_steps(step.ALL_SETUP_WITH_ENV_ARG, set()),
            PhaseEnum.ACT: psr.same_value_for_all_steps(step.ALL_ACT_WITH_ENV_ARG, set()),
            PhaseEnum.BEFORE_ASSERT: psr.same_value_for_all_steps(step.ALL_BEFORE_ASSERT_WITH_ENV_ARG, set()),
            PhaseEnum.ASSERT: psr.same_value_for_all_steps(step.ALL_ASSERT_WITH_ENV_ARG, set()),
            PhaseEnum.CLEANUP: psr.same_value_for_all_steps(step.ALL_CLEANUP_WITH_ENV_ARG, set()),
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
            Arrangement(psr.actor_that_records_a_value_per_step(recorder_for,
                                                                recorder_for_parse_step=psr.no_recording)),
            asrt.anything_goes())
        _check_result(self,
                      expected_phase_2_step_2_names_set,
                      actual_phase_2_step_2_names_set)

    def test_one_symbol_is_defined_in_the_setup_phase(self):
        symbol = NameAndValue('symbol name',
                              'symbol value (not used in test)')
        all_defined_symbols = frozenset((symbol.name,))
        symbol_definition = data_symbol_utils.string_symbol_definition(symbol.name, symbol.value)
        symbol_usages_of_instruction_that_defines_symbol = [symbol_definition]

        expected_phase_2_step_2_names_set = {
            PhaseEnum.SETUP: {
                step.SETUP__VALIDATE_PRE_SDS.step: all_defined_symbols,
                step.SETUP__MAIN.step: set(),
                step.SETUP__VALIDATE_POST_SETUP.step: all_defined_symbols,
            },
            PhaseEnum.ACT: {
                step.ACT__VALIDATE_PRE_SDS.step: all_defined_symbols,
                step.ACT__VALIDATE_POST_SETUP.step: all_defined_symbols,
                step.ACT__EXECUTE.step: all_defined_symbols,
                step.ACT__PREPARE.step: all_defined_symbols,
            },
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
            Arrangement(psr.actor_that_records_a_value_per_step(recorder_for,
                                                                recorder_for_parse_step=psr.no_recording)),
            asrt.anything_goes())
        _check_result(self,
                      expected_phase_2_step_2_names_set,
                      actual_phase_2_step_2_names_set)

    def test_one_symbol_is_defined_in_the_before_assert_phase(self):
        symbol = NameAndValue('symbol name',
                              'symbol value (not used in test)')
        all_defined_symbols = {symbol.name}
        symbol_definition = data_symbol_utils.string_symbol_definition(symbol.name, symbol.value)
        symbol_usages_of_instruction_that_defines_symbol = [symbol_definition]

        expected_phase_2_step_2_names_set = {
            PhaseEnum.SETUP: {
                step.SETUP__VALIDATE_PRE_SDS.step: all_defined_symbols,
                step.SETUP__MAIN.step: set(),
                step.SETUP__VALIDATE_POST_SETUP.step: all_defined_symbols,
            },
            PhaseEnum.ACT: {
                step.ACT__VALIDATE_PRE_SDS.step: all_defined_symbols,
                step.ACT__VALIDATE_POST_SETUP.step: all_defined_symbols,
                step.ACT__EXECUTE.step: set(),
                step.ACT__PREPARE.step: set(),
            },
            PhaseEnum.BEFORE_ASSERT: {
                step.BEFORE_ASSERT__VALIDATE_PRE_SDS.step: all_defined_symbols,
                step.BEFORE_ASSERT__MAIN.step: set(),
                step.BEFORE_ASSERT__VALIDATE_POST_SETUP.step: all_defined_symbols,
            },
            PhaseEnum.ASSERT: {
                step.ASSERT__VALIDATE_PRE_SDS.step: all_defined_symbols,
                step.ASSERT__MAIN.step: all_defined_symbols,
                step.ASSERT__VALIDATE_POST_SETUP.step: all_defined_symbols,
            },
            PhaseEnum.CLEANUP: psr.same_value_for_all_steps(step.ALL_CLEANUP_WITH_ENV_ARG, all_defined_symbols),
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
                before_assert_phase_instruction_that(
                    symbol_usages=do_return(symbol_usages_of_instruction_that_defines_symbol),
                    validate_pre_sds_initial_action=recorder_for(step.BEFORE_ASSERT__VALIDATE_PRE_SDS),
                    main_initial_action=Sequence([
                        recorder_for(step.BEFORE_ASSERT__MAIN),
                        _ActionThatSetsSymbolInSymbolTable(symbol_definition),
                    ]),
                    validate_post_setup_initial_action=recorder_for(step.BEFORE_ASSERT__VALIDATE_POST_SETUP),
                )
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
            Arrangement(psr.actor_that_records_a_value_per_step(recorder_for,
                                                                recorder_for_parse_step=psr.no_recording)),
            asrt.anything_goes())
        _check_result(self,
                      expected_phase_2_step_2_names_set,
                      actual_phase_2_step_2_names_set)

    def test_one_symbol_is_defined_in_the_assert_phase(self):
        symbol = NameAndValue('symbol name',
                              'symbol value (not used in test)')
        all_defined_symbols = {symbol.name}
        symbol_definition = data_symbol_utils.string_symbol_definition(symbol.name, symbol.value)
        symbol_usages_of_instruction_that_defines_symbol = [symbol_definition]

        expected_phase_2_step_2_names_set = {
            PhaseEnum.SETUP: {
                step.SETUP__VALIDATE_PRE_SDS.step: all_defined_symbols,
                step.SETUP__MAIN.step: set(),
                step.SETUP__VALIDATE_POST_SETUP.step: all_defined_symbols,
            },
            PhaseEnum.ACT: {
                step.ACT__VALIDATE_PRE_SDS.step: all_defined_symbols,
                step.ACT__VALIDATE_POST_SETUP.step: all_defined_symbols,
                step.ACT__EXECUTE.step: set(),
                step.ACT__PREPARE.step: set(),
            },
            PhaseEnum.BEFORE_ASSERT: {
                step.BEFORE_ASSERT__VALIDATE_PRE_SDS.step: all_defined_symbols,
                step.BEFORE_ASSERT__MAIN.step: set(),
                step.BEFORE_ASSERT__VALIDATE_POST_SETUP.step: all_defined_symbols,
            },
            PhaseEnum.ASSERT: {
                step.ASSERT__VALIDATE_PRE_SDS.step: all_defined_symbols,
                step.ASSERT__MAIN.step: set(),
                step.ASSERT__VALIDATE_POST_SETUP.step: all_defined_symbols,
            },
            PhaseEnum.CLEANUP: psr.same_value_for_all_steps(step.ALL_CLEANUP_WITH_ENV_ARG, all_defined_symbols),
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
                assert_phase_instruction_that(
                    symbol_usages=do_return(symbol_usages_of_instruction_that_defines_symbol),
                    validate_pre_sds_initial_action=recorder_for(step.ASSERT__VALIDATE_PRE_SDS),
                    main_initial_action=Sequence([
                        recorder_for(step.ASSERT__MAIN),
                        _ActionThatSetsSymbolInSymbolTable(symbol_definition),
                    ]),
                    validate_post_setup_initial_action=recorder_for(step.ASSERT__VALIDATE_POST_SETUP),
                )
            ],
            [
                psr.cleanup_phase_instruction_that_records_a_value_per_step(recorder_for)
            ],
        )
        test__va(
            self,
            test_case,
            Arrangement(psr.actor_that_records_a_value_per_step(recorder_for,
                                                                recorder_for_parse_step=psr.no_recording)),
            asrt.anything_goes())
        _check_result(self,
                      expected_phase_2_step_2_names_set,
                      actual_phase_2_step_2_names_set)

    def test_one_symbol_is_defined_in_the_cleanup_phase(self):
        symbol = NameAndValue('symbol name',
                              'symbol value (not used in test)')
        all_defined_symbols = {symbol.name}
        symbol_definition = data_symbol_utils.string_symbol_definition(symbol.name, symbol.value)
        symbol_usages_of_instruction_that_defines_symbol = [symbol_definition]

        expected_phase_2_step_2_names_set = {
            PhaseEnum.SETUP: {
                step.SETUP__VALIDATE_PRE_SDS.step: all_defined_symbols,
                step.SETUP__MAIN.step: set(),
                step.SETUP__VALIDATE_POST_SETUP.step: all_defined_symbols,
            },
            PhaseEnum.ACT: {
                step.ACT__VALIDATE_PRE_SDS.step: all_defined_symbols,
                step.ACT__VALIDATE_POST_SETUP.step: all_defined_symbols,
                step.ACT__EXECUTE.step: set(),
                step.ACT__PREPARE.step: set(),
            },
            PhaseEnum.BEFORE_ASSERT: {
                step.BEFORE_ASSERT__VALIDATE_PRE_SDS.step: all_defined_symbols,
                step.BEFORE_ASSERT__MAIN.step: set(),
                step.BEFORE_ASSERT__VALIDATE_POST_SETUP.step: all_defined_symbols,
            },
            PhaseEnum.ASSERT: {
                step.ASSERT__VALIDATE_PRE_SDS.step: all_defined_symbols,
                step.ASSERT__MAIN.step: set(),
                step.ASSERT__VALIDATE_POST_SETUP.step: all_defined_symbols,
            },
            PhaseEnum.CLEANUP: {
                step.CLEANUP__VALIDATE_PRE_SDS.step: all_defined_symbols,
                step.CLEANUP__MAIN.step: set(),
            },
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
                cleanup_phase_instruction_that(
                    symbol_usages=do_return(symbol_usages_of_instruction_that_defines_symbol),
                    validate_pre_sds_initial_action=recorder_for(step.CLEANUP__VALIDATE_PRE_SDS),
                    main_initial_action=Sequence([
                        recorder_for(step.CLEANUP__MAIN),
                        _ActionThatSetsSymbolInSymbolTable(symbol_definition),
                    ]),
                )
            ],
        )
        test__va(
            self,
            test_case,
            Arrangement(psr.actor_that_records_a_value_per_step(recorder_for,
                                                                recorder_for_parse_step=psr.no_recording)),
            asrt.anything_goes())
        _check_result(self,
                      expected_phase_2_step_2_names_set,
                      actual_phase_2_step_2_names_set)


class TestPropagationOfSymbolsPredefinedInConfiguration(unittest.TestCase):
    def test_one_symbol_is_predefined(self):
        predefined_symbol = NameAndValue('predefined symbol name',
                                         'predefined string constant symbol value')

        expected_predefined_symbols = SymbolTable({
            predefined_symbol.name: symbol_utils.container(string_resolvers.str_constant(predefined_symbol.value))
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
            Arrangement(psr.actor_that_records_a_value_per_step(recorder_for,
                                                                recorder_for_parse_step=psr.no_recording),
                        predefined_symbols=expected_predefined_symbols),
            asrt.anything_goes())
        _check_result(self,
                      expected_phase_2_step_2_names_set,
                      actual_phase_2_step_2_names_set)

    def test_one_symbol_is_predefined_and_one_symbol_is_defined_in_the_setup_phase(self):
        predefined_symbol = NameAndValue('predefined symbol',
                                         'predefined string constant symbol value')
        defined_symbol = NameAndValue('defined symbol',
                                      'value of symbol defined in the setup phase (not used in this test)')
        predefined_symbols_table = SymbolTable({
            predefined_symbol.name: symbol_utils.container(string_resolvers.str_constant(predefined_symbol.value))
        })
        predefined_symbols = frozenset((predefined_symbol.name,))
        predefined_and_defined_symbols = frozenset((predefined_symbol.name, defined_symbol.name))

        symbol_definition = data_symbol_utils.string_symbol_definition(defined_symbol.name, defined_symbol.value)

        symbol_usages_of_instruction_that_defines_symbol = [symbol_definition]

        expected_phase_2_step_2_names_set = {
            PhaseEnum.SETUP: {
                step.SETUP__VALIDATE_PRE_SDS.step: predefined_and_defined_symbols,
                step.SETUP__MAIN.step: predefined_symbols,
                step.SETUP__VALIDATE_POST_SETUP.step: predefined_and_defined_symbols,
            },
            PhaseEnum.ACT: {
                step.ACT__VALIDATE_PRE_SDS.step: predefined_and_defined_symbols,
                step.ACT__VALIDATE_POST_SETUP.step: predefined_and_defined_symbols,
                step.ACT__PREPARE.step: predefined_and_defined_symbols,
                step.ACT__EXECUTE.step: predefined_and_defined_symbols,
            },
            PhaseEnum.BEFORE_ASSERT: {
                step.BEFORE_ASSERT__VALIDATE_PRE_SDS.step: predefined_and_defined_symbols,
                step.BEFORE_ASSERT__VALIDATE_POST_SETUP.step: predefined_and_defined_symbols,
                step.BEFORE_ASSERT__MAIN.step: predefined_and_defined_symbols,

            },
            PhaseEnum.ASSERT: {
                step.ASSERT__VALIDATE_PRE_SDS.step: predefined_and_defined_symbols,
                step.ASSERT__VALIDATE_POST_SETUP.step: predefined_and_defined_symbols,
                step.ASSERT__MAIN.step: predefined_and_defined_symbols,
            },
            PhaseEnum.CLEANUP: {
                step.CLEANUP__VALIDATE_PRE_SDS.step: predefined_and_defined_symbols,
                step.CLEANUP__MAIN.step: predefined_and_defined_symbols,
            },
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
            Arrangement(
                actor=psr.actor_that_records_a_value_per_step(recorder_for,
                                                              recorder_for_parse_step=psr.no_recording),
                predefined_symbols=predefined_symbols_table),
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
