import unittest

from exactly_lib.execution.phase_step_simple import \
    ALL_SETUP_WITH_ENV_ARG, ALL_ASSERT_WITH_ENV_ARG, ALL_BEFORE_ASSERT_WITH_ENV_ARG, \
    ALL_CLEANUP_WITH_ENV_ARG, ALL_ACT_POST_SDS
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.execution.full_execution.test_resources import execution_check, \
    result_assertions as asrt_full_result
from exactly_lib_test.execution.test_resources.execution_recording.recording2 import PropertyRecorderBuilder, \
    builder_of_test_case_that_records_property_of_env_for_each_step_of_partial_execution, \
    actor_that_records_property_of_env_for_each_step_post_sds
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_mem_buff_size_SHOULD_be_propagated_to_every_instruction_after_conf_phase(
            self):
        # ARRANGE #
        with tmp_dir() as tmp_dir_path:
            expected_mem_buff_size = 72
            actual_recordings = {}
            recorder_builder = PropertyRecorderBuilder(
                get_mem_buff_size,
                actual_recordings)
            test_case_builder = builder_of_test_case_that_records_property_of_env_for_each_step_of_partial_execution(
                recorder_builder)
            test_case = test_case_builder.build()
            actor = actor_that_records_property_of_env_for_each_step_post_sds(recorder_builder)
            configuration_builder = ConfigurationBuilder(tmp_dir_path,
                                                         tmp_dir_path,
                                                         NameAndValue('the actor', actor),
                                                         timeout_in_seconds=30)
            arrangement = execution_check.Arrangement(test_case,
                                                      configuration_builder,
                                                      mem_buff_size=expected_mem_buff_size)
            expectation = execution_check.Expectation(full_result=asrt_full_result.is_pass())
            # ACT & ASSERT #
            execution_check.check(self, arrangement, expectation)
            # ASSERT #
            expected_recordings = dict.fromkeys(ALL_SETUP_WITH_ENV_ARG +
                                                ALL_ACT_POST_SDS +
                                                ALL_BEFORE_ASSERT_WITH_ENV_ARG +
                                                ALL_ASSERT_WITH_ENV_ARG +
                                                ALL_CLEANUP_WITH_ENV_ARG,
                                                expected_mem_buff_size)
            self.assertDictEqual(expected_recordings, actual_recordings)


def get_mem_buff_size(env: InstructionEnvironmentForPreSdsStep) -> int:
    return env.mem_buff_size
