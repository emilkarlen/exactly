import unittest

import types
from operator import attrgetter
from typing import Callable

from exactly_lib.execution import phase_step_simple as step
from exactly_lib.execution.phase_step import SimplePhaseStep
from exactly_lib.test_case.actor import Actor
from exactly_lib.test_case.phase_identifier import PHASES_FOR_PARTIAL_EXECUTION
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that, \
    before_assert_phase_instruction_that, assert_phase_instruction_that, \
    cleanup_phase_instruction_that, act_phase_instruction_with_source
from exactly_lib_test.test_case.actor.test_resources.actor_impls import ActorThatRunsConstantActions
from exactly_lib_test.test_resources import actions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertionBase


class Phase2step2recordedValueAssertion(ValueAssertionBase):
    """ Custom comparison for better error messages. """

    def __init__(self,
                 expected_phase_2_step_2_recorded_value: dict):
        self.expected_phase_2_step_2_recorded_value = expected_phase_2_step_2_recorded_value

    def _apply(self,
               put: unittest.TestCase,
               actual_phase_2_step_2_recorded_value,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(actual_phase_2_step_2_recorded_value, dict,
                             'actual value should be a dictionary')

        for phase in sorted(self.expected_phase_2_step_2_recorded_value.keys(),
                            key=attrgetter('value')):
            put.assertIn(phase, self.expected_phase_2_step_2_recorded_value)
            expected_steps = self.expected_phase_2_step_2_recorded_value[phase]
            actual = actual_phase_2_step_2_recorded_value[phase]
            for expected_step in sorted(expected_steps.keys()):
                put.assertIn(expected_step, actual, 'Phase {}: Missing step: {}'.format(phase, expected_step))
                put.assertEqual(expected_steps[expected_step],
                                actual[expected_step],
                                '{}/{}'.format(phase, expected_step))
                put.assertEqual(len(expected_steps),
                                len(actual),
                                'Actual number of recorded steps for phase {} must not exceed expected'.format(phase))
                put.assertEqual(len(self.expected_phase_2_step_2_recorded_value),
                                len(actual_phase_2_step_2_recorded_value),
                                'Actual number of recorded phases must not exceed expected')
                # To be sure that above code does not miss any case
                put.assertEqual(self.expected_phase_2_step_2_recorded_value,
                                actual_phase_2_step_2_recorded_value,
                                'Recordings per phase and step')


def setup_phase_instruction_that_records_a_value_per_step(recorder_for) -> SetupPhaseInstruction:
    return setup_phase_instruction_that(
        validate_pre_sds_initial_action=recorder_for(step.SETUP__VALIDATE_PRE_SDS),
        main_initial_action=recorder_for(step.SETUP__MAIN),
        validate_post_setup_initial_action=recorder_for(step.SETUP__VALIDATE_POST_SETUP),
    )


def before_assert_phase_instruction_that_records_a_value_per_step(recorder_for) -> BeforeAssertPhaseInstruction:
    return before_assert_phase_instruction_that(
        validate_pre_sds_initial_action=recorder_for(step.BEFORE_ASSERT__VALIDATE_PRE_SDS),
        validate_post_setup_initial_action=recorder_for(step.BEFORE_ASSERT__VALIDATE_POST_SETUP),
        main_initial_action=recorder_for(step.BEFORE_ASSERT__MAIN),
    )


def assert_phase_instruction_that_records_a_value_per_step(recorder_for) -> AssertPhaseInstruction:
    return assert_phase_instruction_that(
        validate_pre_sds_initial_action=recorder_for(step.ASSERT__VALIDATE_PRE_SDS),
        validate_post_setup_initial_action=recorder_for(step.ASSERT__VALIDATE_POST_SETUP),
        main_initial_action=recorder_for(step.ASSERT__MAIN),
    )


def cleanup_phase_instruction_that_records_a_value_per_step(recorder_for) -> CleanupPhaseInstruction:
    return cleanup_phase_instruction_that(
        validate_pre_sds_initial_action=recorder_for(step.CLEANUP__VALIDATE_PRE_SDS),
        main_initial_action=recorder_for(step.CLEANUP__MAIN),
    )


def act_phase_instructions_that_does_nothing():
    return [act_phase_instruction_with_source(LineSequence(1, ('line',)))]


class StepRecordingAction:
    def __init__(self,
                 phase_step: SimplePhaseStep,
                 phase_2_step_2_recorded_value: dict,
                 value_to_record_from_step_arguments_getter: Callable):
        self.value_to_record_from_step_arguments_getter = value_to_record_from_step_arguments_getter
        self.phase_2_step_2_recorded_value = phase_2_step_2_recorded_value
        self.phase_step = phase_step

    def __call__(self, *args, **kwargs):
        value_to_record = self.value_to_record_from_step_arguments_getter(*args, **kwargs)
        self.phase_2_step_2_recorded_value[self.phase_step.phase][self.phase_step.step] = value_to_record


def no_recording(phase_step: SimplePhaseStep):
    return actions.do_nothing


def actor_that_records_a_value_per_step(
        recorder_for_step_with_env: types.FunctionType,
        recorder_for_parse_step: types.FunctionType,
) -> Actor:
    return ActorThatRunsConstantActions(
        parse_atc=recorder_for_parse_step(step.ACT__PARSE),
        validate_pre_sds_initial_action=recorder_for_step_with_env(step.ACT__VALIDATE_PRE_SDS),
        validate_post_setup_initial_action=recorder_for_step_with_env(step.ACT__VALIDATE_POST_SETUP),
        prepare_initial_action=recorder_for_step_with_env(step.ACT__PREPARE),
        execute_initial_action=recorder_for_step_with_env(step.ACT__EXECUTE),
    )


def new_phase_enum_2_empty_dict() -> dict:
    ret_val = {}
    for phase in PHASES_FOR_PARTIAL_EXECUTION:
        ret_val[phase.the_enum] = {}
    return ret_val


def same_value_for_all_steps(phase_step_list, value) -> dict:
    ret_val = {}
    for ps in phase_step_list:
        ret_val[ps.step] = value
    return ret_val
