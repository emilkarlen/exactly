import unittest

from exactly_lib.execution.phase_step_identifiers import phase_step_simple as step
from exactly_lib.execution.phase_step_identifiers.phase_step import SimplePhaseStep
from exactly_lib.test_case.phase_identifier import PhaseEnum
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib_test.execution.partial_execution.test_resources.basic import Arrangement, test__va
from exactly_lib_test.execution.test_resources.execution_recording import phase_step_recordings as psr
from exactly_lib_test.execution.test_resources.test_case_generation import partial_test_case_with_instructions
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_hds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.makeSuite:
    return unittest.makeSuite(TestPropagationOfHomeDirectoryStructureBetweenSteps)


class TestPropagationOfHomeDirectoryStructureBetweenSteps(unittest.TestCase):
    def test(self):
        hds_with_different_sub_dirs = fake_hds()

        expected_phase_2_step_2_names_set = {
            PhaseEnum.SETUP: psr.same_value_for_all_steps(step.ALL_SETUP_WITH_ENV_ARG, hds_with_different_sub_dirs),
            PhaseEnum.ACT: psr.same_value_for_all_steps(step.ALL_ACT_WITH_ENV_ARG, hds_with_different_sub_dirs),
            PhaseEnum.BEFORE_ASSERT: psr.same_value_for_all_steps(step.ALL_BEFORE_ASSERT_WITH_ENV_ARG,
                                                                  hds_with_different_sub_dirs),
            PhaseEnum.ASSERT: psr.same_value_for_all_steps(step.ALL_ASSERT_WITH_ENV_ARG, hds_with_different_sub_dirs),
            PhaseEnum.CLEANUP: psr.same_value_for_all_steps(step.ALL_CLEANUP_WITH_ENV_ARG, hds_with_different_sub_dirs),
        }
        actual_phase_2_step_2_names_set = psr.new_phase_enum_2_empty_dict()

        def recorder_for(phase_step: SimplePhaseStep):
            return psr.StepRecordingAction(phase_step,
                                           actual_phase_2_step_2_names_set,
                                           get_hds_from_instruction_environment)

        test_case = partial_test_case_with_instructions(
            [
                psr.setup_phase_instruction_that_records_a_value_per_step(recorder_for),
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
            Arrangement(psr.act_phase_handling_that_records_a_value_per_step(recorder_for),
                        hds=hds_with_different_sub_dirs),
            asrt.anything_goes())
        self._check_result(expected_phase_2_step_2_names_set,
                           actual_phase_2_step_2_names_set)

    def _check_result(self,
                      expected_phase_2_step_2_recorded_value: dict,
                      actual_phase_2_step_2_recorded_value: dict):
        assertion = psr.Phase2step2recordedValueAssertion(expected_phase_2_step_2_recorded_value)
        assertion.apply_with_message(self,
                                     actual_phase_2_step_2_recorded_value,
                                     'recorded values')


def get_hds_from_instruction_environment(environment: InstructionEnvironmentForPreSdsStep, *args, **kwargs):
    return environment.hds


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
