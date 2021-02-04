import pathlib
import unittest
from typing import Optional

from exactly_lib.execution.phase_step_simple import \
    ALL_SETUP_WITH_ENV_ARG, ALL_ASSERT_WITH_ENV_ARG, ALL_BEFORE_ASSERT_WITH_ENV_ARG, \
    ALL_CLEANUP_WITH_ENV_ARG, ALL_ACT_POST_SDS
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder, ConfigurationPhaseInstruction
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.result import svh
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.execution.full_execution.test_resources import execution_check, \
    result_assertions as asrt_full_result
from exactly_lib_test.execution.test_resources.execution_recording.recording2 import PropertyRecorderBuilder, \
    builder_of_test_case_that_records_property_of_env_for_each_step_of_partial_execution, \
    actor_that_records_property_of_env_for_each_step_post_sds


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


def _current_dir() -> pathlib.Path:
    return pathlib.Path().resolve()


class Test(unittest.TestCase):
    def test_WHEN_no_instruction_sets_timeout_THEN_the_default_timeout_SHOULD_be_propagated_to_instructions_and_act_phase(
            self):
        # ARRANGE #
        default_timeout = 72
        actual_recordings = {}
        recorder_builder = PropertyRecorderBuilder(
            get_timeout_in_seconds,
            actual_recordings)
        test_case = builder_of_test_case_that_records_property_of_env_for_each_step_of_partial_execution(
            recorder_builder).build()
        actor = actor_that_records_property_of_env_for_each_step_post_sds(
            recorder_builder)
        default_hds_dir = _current_dir()
        configuration_builder_with_default_timeout = ConfigurationBuilder(default_hds_dir,
                                                                          default_hds_dir,
                                                                          NameAndValue('the actor', actor),
                                                                          default_timeout)
        arrangement = execution_check.Arrangement(test_case,
                                                  configuration_builder_with_default_timeout)
        expectation = execution_check.Expectation(full_result=asrt_full_result.is_pass())
        # ACT & ASSERT #
        execution_check.check(self, arrangement, expectation)
        # ASSERT #
        expected_recordings = dict.fromkeys(ALL_SETUP_WITH_ENV_ARG +
                                            ALL_ACT_POST_SDS +
                                            ALL_BEFORE_ASSERT_WITH_ENV_ARG +
                                            ALL_ASSERT_WITH_ENV_ARG +
                                            ALL_CLEANUP_WITH_ENV_ARG,
                                            default_timeout)
        self.assertDictEqual(expected_recordings, actual_recordings)

    def test_WHEN_an_instruction_sets_timeout_THEN_the_that_timeout_SHOULD_be_propagated_to_instructions_and_act_phase(
            self):
        # ARRANGE #

        expected_timeout = 87
        actual_recordings = {}
        recorder_builder = PropertyRecorderBuilder(
            get_timeout_in_seconds,
            actual_recordings)
        test_case_builder = builder_of_test_case_that_records_property_of_env_for_each_step_of_partial_execution(
            recorder_builder)
        test_case_builder.configuration_phase = [_ConfigurationPhaseInstructionThatSetsTimeoutTo(expected_timeout)]
        test_case = test_case_builder.build()
        actor = actor_that_records_property_of_env_for_each_step_post_sds(
            recorder_builder)
        default_hds_dir = _current_dir()
        configuration_builder_with_default_timeout = ConfigurationBuilder(default_hds_dir,
                                                                          default_hds_dir,
                                                                          NameAndValue('the actor', actor),
                                                                          expected_timeout)
        arrangement = execution_check.Arrangement(test_case,
                                                  configuration_builder_with_default_timeout)
        expectation = execution_check.Expectation(full_result=asrt_full_result.is_pass())
        # ACT & ASSERT #
        execution_check.check(self, arrangement, expectation)
        # ASSERT #
        expected_recordings = dict.fromkeys(ALL_SETUP_WITH_ENV_ARG +
                                            ALL_ACT_POST_SDS +
                                            ALL_BEFORE_ASSERT_WITH_ENV_ARG +
                                            ALL_ASSERT_WITH_ENV_ARG +
                                            ALL_CLEANUP_WITH_ENV_ARG,
                                            expected_timeout)
        self.assertDictEqual(expected_recordings, actual_recordings)


class _ConfigurationPhaseInstructionThatSetsTimeoutTo(ConfigurationPhaseInstruction):
    def __init__(self, timeout):
        self.timeout = timeout

    def main(self, configuration_builder: ConfigurationBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        configuration_builder.set_timeout_in_seconds(self.timeout)
        return svh.new_svh_success()


def get_timeout_in_seconds(env: InstructionEnvironmentForPreSdsStep) -> Optional[int]:
    return env.proc_exe_settings.timeout_in_seconds
