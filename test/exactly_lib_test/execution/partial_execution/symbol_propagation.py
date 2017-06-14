import types
import unittest

from exactly_lib.execution.phase_step_identifiers import phase_step_simple as step
from exactly_lib.execution.phase_step_identifiers.phase_step import SimplePhaseStep
from exactly_lib.symbol.symbol_usage import SymbolDefinition
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.test_case.phase_identifier import PhaseEnum, PHASES_FOR_PARTIAL_EXECUTION
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.execution.partial_execution.test_resources.basic import test__va
from exactly_lib_test.execution.test_resources.act_source_executor import \
    ActSourceAndExecutorConstructorThatRunsConstantActions
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that, \
    before_assert_phase_instruction_that, assert_phase_instruction_that, \
    cleanup_phase_instruction_that, act_phase_instruction_with_source
from exactly_lib_test.execution.test_resources.test_case_generation import partial_test_case_with_instructions
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.test_resources.functions import Sequence
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.makeSuite:
    return unittest.makeSuite(TestPropagationOfSymbolBetweenPhases)


class TestPropagationOfSymbolBetweenPhases(unittest.TestCase):
    def test_symbol_table_should_be_empty_when_no_symbols_are_defined(self):
        expected_phase_2_step_2_names_set = {
            PhaseEnum.SETUP: _for_steps(step.ALL_SETUP_WITH_ENV_ARG, frozenset()),
            PhaseEnum.ACT: _for_steps(step.ALL_ACT_WITH_ENV_ARG, frozenset()),
            PhaseEnum.BEFORE_ASSERT: _for_steps(step.ALL_BEFORE_ASSERT_WITH_ENV_ARG, frozenset()),
            PhaseEnum.ASSERT: _for_steps(step.ALL_ASSERT_WITH_ENV_ARG, frozenset()),
            PhaseEnum.CLEANUP: _for_steps(step.ALL_CLEANUP_WITH_ENV_ARG, frozenset()),
        }
        actual_phase_2_step_2_names_set = _new_phase_enum_2_empty_dict()

        def recorder_for(phase_step: SimplePhaseStep):
            return _StepRecordingAction(phase_step, actual_phase_2_step_2_names_set)

        test_case = partial_test_case_with_instructions(
            [
                _setup_phase_instruction_that_records_each_step_with_symbols(recorder_for)
            ],
            _act_phase_instructions_that_are_not_relevant_to_this_test(),
            [
                _before_assert_phase_instruction_that_records_each_step_with_symbols(recorder_for)
            ],
            [
                _assert_phase_instruction_that_records_each_step_with_symbols(recorder_for)
            ],
            [
                _cleanup_phase_instruction_that_records_each_step_with_symbols(recorder_for)
            ],
        )
        test__va(
            self,
            test_case,
            _act_phase_handling_that_records_existence_of_var_in_global_env(recorder_for),
            asrt.anything_goes(),
            is_keep_execution_directory_root=False)
        self._check_result(expected_phase_2_step_2_names_set,
                           actual_phase_2_step_2_names_set)

    def test_one_symbol_is_defined_in_the_setup_phase(self):
        symbol_name = 'symbol_name'
        all_defined_symbols = frozenset((symbol_name,))
        symbol_definition = symbol_utils.string_symbol_definition(symbol_name, 'symbol value (not used in test)')
        symbol_usages_of_instruction_that_defines_symbol = [symbol_definition]
        expected_phase_2_step_2_names_set = {
            PhaseEnum.SETUP: {
                step.SETUP__VALIDATE_PRE_SDS.step: all_defined_symbols,
                step.SETUP__MAIN.step: frozenset(),
                step.SETUP__VALIDATE_POST_SETUP.step: all_defined_symbols,
            },
            PhaseEnum.ACT: _for_steps(step.ALL_ACT_WITH_ENV_ARG, all_defined_symbols),
            PhaseEnum.BEFORE_ASSERT: _for_steps(step.ALL_BEFORE_ASSERT_WITH_ENV_ARG, all_defined_symbols),
            PhaseEnum.ASSERT: _for_steps(step.ALL_ASSERT_WITH_ENV_ARG, all_defined_symbols),
            PhaseEnum.CLEANUP: _for_steps(step.ALL_CLEANUP_WITH_ENV_ARG, all_defined_symbols),
        }
        actual_phase_2_step_2_names_set = _new_phase_enum_2_empty_dict()

        def recorder_for(phase_step: SimplePhaseStep):
            return _StepRecordingAction(phase_step, actual_phase_2_step_2_names_set)

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
            _act_phase_instructions_that_are_not_relevant_to_this_test(),
            [
                _before_assert_phase_instruction_that_records_each_step_with_symbols(recorder_for)
            ],
            [
                _assert_phase_instruction_that_records_each_step_with_symbols(recorder_for)
            ],
            [
                _cleanup_phase_instruction_that_records_each_step_with_symbols(recorder_for)
            ],
        )
        test__va(
            self,
            test_case,
            _act_phase_handling_that_records_existence_of_var_in_global_env(recorder_for),
            asrt.anything_goes(),
            is_keep_execution_directory_root=False)
        self._check_result(expected_phase_2_step_2_names_set,
                           actual_phase_2_step_2_names_set)

    def _check_result(self,
                      expected_phase_2_step_2_names_set: dict,
                      actual_phase_2_step_2_names_set: dict):
        """
        Custom comparison for better error messages.
        """
        for phase in expected_phase_2_step_2_names_set:
            self.assertIn(phase, expected_phase_2_step_2_names_set)
            expected = expected_phase_2_step_2_names_set[phase]
            actual = actual_phase_2_step_2_names_set[phase]
            for step in expected:
                self.assertIn(step, actual, 'Phase {}: Missing step: {}'.format(phase, step))
                self.assertEqual(expected[step],
                                 actual[step],
                                 'Phase {}/Step {}'.format(phase, step))
            self.assertEqual(len(expected),
                             len(actual),
                             'Actual number of recorded steps for phase {} must not exceed expected'.format(phase))
        self.assertEqual(len(expected_phase_2_step_2_names_set),
                         len(actual_phase_2_step_2_names_set),
                         'Actual number of recorded phases must not exceed expected')
        # To be sure that above code does not miss any case
        self.assertEqual(expected_phase_2_step_2_names_set,
                         actual_phase_2_step_2_names_set,
                         'Recordings per phase and step')


def _setup_phase_instruction_that_records_each_step_with_symbols(recorder_for) -> SetupPhaseInstruction:
    return setup_phase_instruction_that(
        validate_pre_sds_initial_action=recorder_for(step.SETUP__VALIDATE_PRE_SDS),
        main_initial_action=recorder_for(step.SETUP__MAIN),
        validate_post_setup_initial_action=recorder_for(step.SETUP__VALIDATE_POST_SETUP),
    )


def _before_assert_phase_instruction_that_records_each_step_with_symbols(recorder_for) -> BeforeAssertPhaseInstruction:
    return before_assert_phase_instruction_that(
        validate_pre_sds_initial_action=recorder_for(step.BEFORE_ASSERT__VALIDATE_PRE_SDS),
        validate_post_setup_initial_action=recorder_for(step.BEFORE_ASSERT__VALIDATE_POST_SETUP),
        main_initial_action=recorder_for(step.BEFORE_ASSERT__MAIN),
    )


def _assert_phase_instruction_that_records_each_step_with_symbols(recorder_for) -> AssertPhaseInstruction:
    return assert_phase_instruction_that(
        validate_pre_sds_initial_action=recorder_for(step.ASSERT__VALIDATE_PRE_SDS),
        validate_post_setup_initial_action=recorder_for(step.ASSERT__VALIDATE_POST_SETUP),
        main_initial_action=recorder_for(step.ASSERT__MAIN),
    )


def _cleanup_phase_instruction_that_records_each_step_with_symbols(recorder_for) -> CleanupPhaseInstruction:
    return cleanup_phase_instruction_that(
        validate_pre_sds_initial_action=recorder_for(step.CLEANUP__VALIDATE_PRE_SDS),
        main_initial_action=recorder_for(step.CLEANUP__MAIN),
    )


def _act_phase_instructions_that_are_not_relevant_to_this_test():
    return [act_phase_instruction_with_source(LineSequence(1, ('line',)))]


class _StepRecordingAction:
    def __init__(self,
                 phase_step: SimplePhaseStep,
                 phase_step_dict: dict):
        self.phase_step_dict = phase_step_dict
        self.phase_step = phase_step

    def __call__(self, environment: InstructionEnvironmentForPreSdsStep, *args, **kwargs):
        self.phase_step_dict[self.phase_step.phase][self.phase_step.step] = environment.symbols.names_set


class _ActionThatSetsSymbolInSymbolTable:
    def __init__(self, symbol: SymbolDefinition):
        self.symbol = symbol

    def __call__(self, environment: InstructionEnvironmentForPreSdsStep, *args, **kwargs):
        environment.symbols.put(self.symbol.name,
                                self.symbol.value_container)


def _act_phase_handling_that_records_existence_of_var_in_global_env(
        recorder_for_step: types.FunctionType) -> ActPhaseHandling:
    return ActPhaseHandling(ActSourceAndExecutorConstructorThatRunsConstantActions(
        validate_pre_sds_initial_action=recorder_for_step(step.ACT__VALIDATE_PRE_SDS),
        validate_post_setup_initial_action=recorder_for_step(step.ACT__VALIDATE_POST_SETUP),
        prepare_initial_action=recorder_for_step(step.ACT__PREPARE),
        execute_initial_action=recorder_for_step(step.ACT__EXECUTE),
    ))


def _new_phase_enum_2_empty_dict() -> dict:
    ret_val = {}
    for phase in PHASES_FOR_PARTIAL_EXECUTION:
        ret_val[phase.the_enum] = {}
    return ret_val


def _for_steps(phase_step_list, value) -> dict:
    ret_val = {}
    for ps in phase_step_list:
        ret_val[ps.step] = value
    return ret_val


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
