"""
Utilities to record an attribute associated to execution steps to a dictionary
"""
import types

from exactly_lib.execution import phase_step_simple as step
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.act_phase_handling import ActionToCheckExecutorParser
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that, \
    assert_phase_instruction_that, before_assert_phase_instruction_that, cleanup_phase_instruction_that
from exactly_lib_test.test_case.act_phase_handling.test_resources.act_source_and_executor_constructors import \
    ActionToCheckExecutorParserThatRunsConstantActions
from exactly_lib_test.test_case.test_resources.test_case_doc import TestCaseWithOnlyInstructionElementsBuilder, \
    InstructionElementGenerator


class PropertyRecorderBuilder:
    """
    Builder for recording to a given recorder, a given property,
    for different keys.
    """

    def __init__(self, property_getter: types.FunctionType, recorder: dict):
        self.property_getter = property_getter
        self.recorder = recorder

    def of_first_arg(self, key) -> types.FunctionType:
        def ret_val(first_arg, *args, **kwargs):
            self.recorder[key] = self.property_getter(first_arg)

        return ret_val


def builder_of_test_case_that_records_property_of_env_for_each_step_of_partial_execution(
        property_recorder: PropertyRecorderBuilder) -> TestCaseWithOnlyInstructionElementsBuilder:
    builder = TestCaseWithOnlyInstructionElementsBuilder()
    builder.setup_phase = [setup_phase_instruction_that_records_property_of_env_for_each_step(property_recorder)]
    builder.before_assert_phase = [before_assert_phase_instruction_that_records_property_of_env_for_each_step(
        property_recorder)]
    builder.assert_phase = [assert_phase_instruction_that_records_property_of_env_for_each_step(property_recorder)]
    builder.cleanup_phase = [cleanup_phase_instruction_that_records_property_of_env_for_each_step(property_recorder)]
    return builder


def test_case_that_records_property_of_env_for_each_step_of_partial_execution(
        property_recorder: PropertyRecorderBuilder) -> test_case_doc.TestCase:
    element_generator = InstructionElementGenerator()

    return test_case_doc.TestCase(
        element_generator.section_contents([]),
        element_generator.section_contents([
            setup_phase_instruction_that_records_property_of_env_for_each_step(property_recorder)
        ]),
        element_generator.section_contents([]),
        element_generator.section_contents([before_assert_phase_instruction_that_records_property_of_env_for_each_step(
            property_recorder)]
        ),
        element_generator.section_contents([
            assert_phase_instruction_that_records_property_of_env_for_each_step(property_recorder)
        ]),
        element_generator.section_contents([
            cleanup_phase_instruction_that_records_property_of_env_for_each_step(property_recorder)
        ]),

    )


def actor_that_records_property_of_env_for_each_step_w_env_arg(
        property_recorder: PropertyRecorderBuilder) -> ActionToCheckExecutorParser:
    return ActionToCheckExecutorParserThatRunsConstantActions(
        validate_pre_sds_initial_action=property_recorder.of_first_arg(step.ACT__VALIDATE_PRE_SDS),
        validate_post_setup_initial_action=property_recorder.of_first_arg(step.ACT__VALIDATE_POST_SETUP),
        prepare_initial_action=property_recorder.of_first_arg(step.ACT__PREPARE),
        execute_initial_action=property_recorder.of_first_arg(step.ACT__EXECUTE),
    )


def actor_that_records_property_of_env_for_each_step_post_sds(
        property_recorder: PropertyRecorderBuilder) -> ActionToCheckExecutorParser:
    return ActionToCheckExecutorParserThatRunsConstantActions(
        validate_post_setup_initial_action=property_recorder.of_first_arg(step.ACT__VALIDATE_POST_SETUP),
        prepare_initial_action=property_recorder.of_first_arg(step.ACT__PREPARE),
        execute_initial_action=property_recorder.of_first_arg(step.ACT__EXECUTE),
    )


def setup_phase_instruction_that_records_property_of_env_for_each_step(
        property_recorder: PropertyRecorderBuilder) -> SetupPhaseInstruction:
    return setup_phase_instruction_that(
        validate_pre_sds_initial_action=property_recorder.of_first_arg(step.SETUP__VALIDATE_PRE_SDS),
        validate_post_setup_initial_action=property_recorder.of_first_arg(step.SETUP__VALIDATE_POST_SETUP),
        main_initial_action=property_recorder.of_first_arg(step.SETUP__MAIN))


def before_assert_phase_instruction_that_records_property_of_env_for_each_step(
        property_recorder: PropertyRecorderBuilder) -> BeforeAssertPhaseInstruction:
    return before_assert_phase_instruction_that(
        validate_pre_sds_initial_action=property_recorder.of_first_arg(step.BEFORE_ASSERT__VALIDATE_PRE_SDS),
        validate_post_setup_initial_action=property_recorder.of_first_arg(step.BEFORE_ASSERT__VALIDATE_POST_SETUP),
        main_initial_action=property_recorder.of_first_arg(step.BEFORE_ASSERT__MAIN))


def assert_phase_instruction_that_records_property_of_env_for_each_step(
        property_recorder: PropertyRecorderBuilder) -> AssertPhaseInstruction:
    return assert_phase_instruction_that(
        validate_pre_sds_initial_action=property_recorder.of_first_arg(step.ASSERT__VALIDATE_PRE_SDS),
        validate_post_setup_initial_action=property_recorder.of_first_arg(step.ASSERT__VALIDATE_POST_SETUP),
        main_initial_action=property_recorder.of_first_arg(step.ASSERT__MAIN))


def cleanup_phase_instruction_that_records_property_of_env_for_each_step(
        property_recorder: PropertyRecorderBuilder) -> CleanupPhaseInstruction:
    return cleanup_phase_instruction_that(
        validate_pre_sds_initial_action=property_recorder.of_first_arg(step.CLEANUP__VALIDATE_PRE_SDS),
        main_initial_action=property_recorder.of_first_arg(step.CLEANUP__MAIN))
