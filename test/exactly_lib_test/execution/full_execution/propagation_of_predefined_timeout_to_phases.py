import pathlib
import unittest
from typing import Optional

from exactly_lib.execution.phase_step_simple import \
    ALL_SETUP_WITH_ENV_ARG, ALL_ASSERT_WITH_ENV_ARG, ALL_BEFORE_ASSERT_WITH_ENV_ARG, \
    ALL_CLEANUP_WITH_ENV_ARG, ALL_ACT_POST_SDS
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.execution.full_execution.test_resources import execution_check, \
    result_assertions as asrt_full_result
from exactly_lib_test.execution.test_resources import predefined_properties
from exactly_lib_test.execution.test_resources.execution_recording.recording2 import PropertyRecorderBuilder, \
    builder_of_test_case_that_records_property_of_env_for_each_step_of_partial_execution, \
    actor_that_records_property_of_env_for_each_step_post_sds


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


def _current_dir() -> pathlib.Path:
    return pathlib.Path().resolve()


class Test(unittest.TestCase):
    def test_timeout_in_predefined_properties_SHOULD_be_propagated_to_partial_execution(
            self):
        # ARRANGE #
        default_timeout = 72
        actual_recordings = {}
        recorder_builder = PropertyRecorderBuilder(
            _get_timeout_in_seconds,
            actual_recordings)
        test_case = builder_of_test_case_that_records_property_of_env_for_each_step_of_partial_execution(
            recorder_builder).build()
        actor = actor_that_records_property_of_env_for_each_step_post_sds(
            recorder_builder)
        default_hds_dir = _current_dir()
        configuration_builder_with_default_timeout = ConfigurationBuilder(default_hds_dir,
                                                                          default_hds_dir,
                                                                          NameAndValue('the actor', actor))
        arrangement = execution_check.Arrangement(
            test_case,
            configuration_builder_with_default_timeout,
            predefined_properties=predefined_properties.new_w_empty_defaults(
                timeout_in_seconds=default_timeout
            )
        )
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


def _get_timeout_in_seconds(env: InstructionEnvironmentForPreSdsStep) -> Optional[int]:
    return env.proc_exe_settings.timeout_in_seconds
