import pathlib
import unittest

from exactly_lib.execution.phase_step_identifiers.phase_step_simple import ALL_SETUP, ALL_ASSERT, ALL_BEFORE_ASSERT, \
    ALL_CLEANUP
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder, ConfigurationPhaseInstruction
from exactly_lib.test_case.phases.result import sh
from exactly_lib_test.execution.full_execution.test_resources import execution_check
from exactly_lib_test.execution.test_resources import full_result_assertions
from exactly_lib_test.execution.test_resources.execution_recording.recording2 import PropertyRecorderBuilder, \
    test_case_that_records_property_of_env_for_each_step_of_partial_execution, \
    act_phase_handling_that_records_property_of_constructor_argument


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


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
            InstructionEnvironmentForPreSdsStep.timeout_in_seconds.fget,
            actual_recordings)
        test_case = test_case_that_records_property_of_env_for_each_step_of_partial_execution(recorder_builder).build()
        act_phase_handling = act_phase_handling_that_records_property_of_constructor_argument(ACT_EXE_CONSTRUCTOR,
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
            InstructionEnvironmentForPreSdsStep.timeout_in_seconds.fget,
            actual_recordings)
        test_case_builder = test_case_that_records_property_of_env_for_each_step_of_partial_execution(recorder_builder)
        test_case_builder.configuration_phase = [_ConfigurationPhaseInstructionThatSetsTimeoutTo(expected_timeout)]
        test_case = test_case_builder.build()
        act_phase_handling = act_phase_handling_that_records_property_of_constructor_argument(ACT_EXE_CONSTRUCTOR,
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
