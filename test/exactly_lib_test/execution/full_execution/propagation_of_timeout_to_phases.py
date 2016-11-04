import pathlib
import types
import unittest

from exactly_lib.execution import phase_step_simple as step
from exactly_lib.execution.act_phase import ActPhaseHandling
from exactly_lib.execution.phase_step_simple import ALL_SETUP, ALL_ASSERT, ALL_BEFORE_ASSERT, ALL_CLEANUP
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPreEdsStep
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder, ConfigurationPhaseInstruction
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib_test.execution.full_execution.test_resources import execution_check
from exactly_lib_test.execution.test_resources import full_result_assertions
from exactly_lib_test.execution.test_resources.act_source_executor import \
    ActSourceAndExecutorConstructorThatRunsConstantActions
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that, \
    assert_phase_instruction_that, before_assert_phase_instruction_that, cleanup_phase_instruction_that
from exactly_lib_test.test_case.test_resources.test_case_doc import TestCaseWithOnlyInstructionElementsBuilder


def _current_dir() -> pathlib.Path:
    return pathlib.Path().resolve()


ACT_EXE_CONSTRUCTOR = 'act/construct-executor'


class Test(unittest.TestCase):
    def test_WHEN_no_instruction_sets_timeout_THEN_the_default_timeout_SHOULD_be_propagated_to_instructions_and_act_phase(
            self):
        # ARRANGE #
        default_timeout = 72
        actual_recordings = {}
        recorder_builder = PropertyRecorderBuilder(
            GlobalEnvironmentForPreEdsStep.timeout_in_seconds.fget,
            actual_recordings)
        test_case = _test_case_that_records_for_each_step_of_partial_execution(recorder_builder).build()
        act_phase_handling = _act_phase_handling_that_records_property_of_constructor_argument(ACT_EXE_CONSTRUCTOR,
                                                                                               recorder_builder)
        configuration_builder_with_default_timeout = ConfigurationBuilder(_current_dir(),
                                                                          act_phase_handling,
                                                                          default_timeout)
        arrangement = execution_check.Arrangement(test_case,
                                                  configuration_builder_with_default_timeout)
        expectation = execution_check.Expectation(full_result=full_result_assertions.is_pass)
        # ACT & ASSERT #
        execution_check.check(self, arrangement, expectation)
        # ASSERT #
        expected_recordings = dict.fromkeys(ALL_SETUP +
                                            (ACT_EXE_CONSTRUCTOR,) +
                                            ALL_BEFORE_ASSERT +
                                            ALL_ASSERT +
                                            ALL_CLEANUP,
                                            default_timeout)
        self.assertDictEqual(expected_recordings, actual_recordings)

    def test_WHEN_an_instruction_sets_timeout_THEN_the_that_timeout_SHOULD_be_propagated_to_instructions_and_act_phase(
            self):
        # ARRANGE #
        expected_timeout = 87
        actual_recordings = {}
        recorder_builder = PropertyRecorderBuilder(
            GlobalEnvironmentForPreEdsStep.timeout_in_seconds.fget,
            actual_recordings)
        test_case_builder = _test_case_that_records_for_each_step_of_partial_execution(recorder_builder)
        test_case_builder.configuration_phase = [_ConfigurationPhaseInstructionThatSetsTimeoutTo(expected_timeout)]
        test_case = test_case_builder.build()
        act_phase_handling = _act_phase_handling_that_records_property_of_constructor_argument(ACT_EXE_CONSTRUCTOR,
                                                                                               recorder_builder)
        configuration_builder_with_default_timeout = ConfigurationBuilder(_current_dir(),
                                                                          act_phase_handling,
                                                                          expected_timeout)
        arrangement = execution_check.Arrangement(test_case,
                                                  configuration_builder_with_default_timeout)
        expectation = execution_check.Expectation(full_result=full_result_assertions.is_pass)
        # ACT & ASSERT #
        execution_check.check(self, arrangement, expectation)
        # ASSERT #
        expected_recordings = dict.fromkeys(ALL_SETUP +
                                            (ACT_EXE_CONSTRUCTOR,) +
                                            ALL_BEFORE_ASSERT +
                                            ALL_ASSERT +
                                            ALL_CLEANUP,
                                            expected_timeout)
        self.assertDictEqual(expected_recordings, actual_recordings)


class _ConfigurationPhaseInstructionThatSetsTimeoutTo(ConfigurationPhaseInstruction):
    def __init__(self, timeout):
        self.timeout = timeout

    def main(self, configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        configuration_builder.set_timeout_in_seconds(self.timeout)
        return sh.new_sh_success()


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


def _test_case_that_records_for_each_step_of_partial_execution(
        property_recorder: PropertyRecorderBuilder) -> TestCaseWithOnlyInstructionElementsBuilder:
    builder = TestCaseWithOnlyInstructionElementsBuilder()
    builder.setup_phase = [setup_phase_instruction_that_records_for_each_step(property_recorder)]
    builder.before_assert_phase = [before_assert_phase_instruction_that_records_for_each_step(property_recorder)]
    builder.assert_phase = [assert_phase_instruction_that_records_for_each_step(property_recorder)]
    builder.cleanup_phase = [cleanup_phase_instruction_that_records_for_each_step(property_recorder)]
    return builder


def _act_phase_handling_that_records_property_of_constructor_argument(
        key: str,
        property_recorder: PropertyRecorderBuilder) -> ActPhaseHandling:
    return ActPhaseHandling(ActSourceAndExecutorConstructorThatRunsConstantActions(
        apply_action_before_executor_is_constructed=property_recorder.of_first_arg(key)
    ))


def setup_phase_instruction_that_records_for_each_step(
        property_recorder: PropertyRecorderBuilder) -> SetupPhaseInstruction:
    return setup_phase_instruction_that(
        validate_pre_eds_initial_action=property_recorder.of_first_arg(step.SETUP__VALIDATE_PRE_EDS),
        validate_post_setup_initial_action=property_recorder.of_first_arg(step.SETUP__VALIDATE_POST_SETUP),
        main_initial_action=property_recorder.of_first_arg(step.SETUP__MAIN))


def before_assert_phase_instruction_that_records_for_each_step(
        property_recorder: PropertyRecorderBuilder) -> BeforeAssertPhaseInstruction:
    return before_assert_phase_instruction_that(
        validate_pre_eds_initial_action=property_recorder.of_first_arg(step.BEFORE_ASSERT__VALIDATE_PRE_EDS),
        validate_post_setup_initial_action=property_recorder.of_first_arg(step.BEFORE_ASSERT__VALIDATE_POST_SETUP),
        main_initial_action=property_recorder.of_first_arg(step.BEFORE_ASSERT__MAIN))


def assert_phase_instruction_that_records_for_each_step(
        property_recorder: PropertyRecorderBuilder) -> AssertPhaseInstruction:
    return assert_phase_instruction_that(
        validate_pre_eds_initial_action=property_recorder.of_first_arg(step.ASSERT__VALIDATE_PRE_EDS),
        validate_post_setup_initial_action=property_recorder.of_first_arg(step.ASSERT__VALIDATE_POST_SETUP),
        main_initial_action=property_recorder.of_first_arg(step.ASSERT__MAIN))


def cleanup_phase_instruction_that_records_for_each_step(
        property_recorder: PropertyRecorderBuilder) -> CleanupPhaseInstruction:
    return cleanup_phase_instruction_that(
        validate_pre_eds_initial_action=property_recorder.of_first_arg(step.CLEANUP__VALIDATE_PRE_EDS),
        main_initial_action=property_recorder.of_first_arg(step.CLEANUP__MAIN))
