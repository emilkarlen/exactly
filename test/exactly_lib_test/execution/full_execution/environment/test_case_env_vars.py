import unittest
from typing import Dict, Optional, Mapping

from exactly_lib.execution import phase_step
from exactly_lib.execution.full_execution.result import FullExeResultStatus
from exactly_lib.execution.phase_step import PhaseStep
from exactly_lib.tcfs.path_relativity import RelHdsOptionType
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.act.actor import Actor
from exactly_lib.test_case.phases.act.execution_input import AtcExecutionInput
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.util import functional
from exactly_lib.util.file_utils.std import StdOutputFiles
from exactly_lib_test.execution.full_execution.test_resources.test_case_base import FullExecutionTestCaseBase
from exactly_lib_test.execution.test_resources import recorder as instr_setup
from exactly_lib_test.execution.test_resources.instruction_test_resources import before_assert_phase_instruction_that, \
    assert_phase_instruction_that, cleanup_phase_instruction_that, \
    configuration_phase_instruction_that
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that
from exactly_lib_test.execution.test_resources.test_case_generation import full_test_case_with_instructions
from exactly_lib_test.test_case.actor.test_resources.actor_impls import ActorThatRunsConstantActions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TheTest(),
    ])


class TheTest(unittest.TestCase):
    def runTest(self):
        TestExecutor(self).execute()


class TestExecutor(FullExecutionTestCaseBase):
    def __init__(self,
                 put: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False,
                 ):
        self._expected_environ = {
            'MY_VAR': 'MY_VAR_VALUE'
        }
        super().__init__(put,
                         dbg_do_not_delete_dir_structure,
                         environ=dict(self._expected_environ))
        self.recorder = instr_setup.Recorder()

    def _actor(self) -> Actor:
        return ActorThatRunsConstantActions(
            validate_pre_sds_initial_action=_RecordEnvVars(
                self.recorder,
                phase_step.ACT__VALIDATE_PRE_SDS).call,
            validate_post_setup_initial_action=_RecordEnvVars(
                self.recorder,
                phase_step.ACT__VALIDATE_POST_SETUP).call,
            prepare_initial_action=_RecordEnvVars(
                self.recorder,
                phase_step.ACT__PREPARE).call,
            execute_initial_action=_RecordEnvVars(
                self.recorder,
                phase_step.ACT__EXECUTE).as_execute_initial_action)

    def _test_case(self) -> test_case_doc.TestCase:
        return full_test_case_with_instructions(
            [
                configuration_phase_instruction_that(
                    main_initial_action=_ConfigurationPhaseActionThatSetsHdsCaseDirToParent()),
                configuration_phase_instruction_that(
                    main_initial_action=_ConfigurationPhaseActionThatSetsHdsActDirToParentParent())
            ],
            [setup_phase_instruction_that(
                validate_pre_sds_initial_action=_RecordEnvVars(self.recorder,
                                                               phase_step.SETUP__VALIDATE_PRE_SDS).call,
                validate_post_setup_initial_action=_RecordEnvVars(self.recorder,
                                                                  phase_step.SETUP__VALIDATE_POST_SETUP).call,
                main_initial_action=_RecordEnvVars(self.recorder,
                                                   phase_step.SETUP__MAIN).setup_main)
            ],
            [],
            [before_assert_phase_instruction_that(
                validate_pre_sds_initial_action=_RecordEnvVars(self.recorder,
                                                               phase_step.BEFORE_ASSERT__VALIDATE_PRE_SDS).call,
                validate_post_setup_initial_action=_RecordEnvVars(self.recorder,
                                                                  phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP).call,
                main_initial_action=_RecordEnvVars(self.recorder,
                                                   phase_step.BEFORE_ASSERT__MAIN).non_setup_main)
            ],
            [assert_phase_instruction_that(
                validate_pre_sds_initial_action=_RecordEnvVars(self.recorder,
                                                               phase_step.ASSERT__VALIDATE_PRE_SDS).call,
                validate_post_setup_initial_action=_RecordEnvVars(self.recorder,
                                                                  phase_step.ASSERT__VALIDATE_POST_SETUP).call,
                main_initial_action=_RecordEnvVars(self.recorder,
                                                   phase_step.ASSERT__MAIN).non_setup_main)
            ],
            [cleanup_phase_instruction_that(
                validate_pre_sds_initial_action=_RecordEnvVars(self.recorder,
                                                               phase_step.CLEANUP__VALIDATE_PRE_SDS).call,
                main_initial_action=_RecordEnvVars(self.recorder,
                                                   phase_step.CLEANUP__MAIN).non_setup_main)
            ],
        )

    def __assert_expected_recorded_variables(self):
        non_setup_main_step = {
            SOURCE__INSTR_ENVIRONMENT: self._expected_environ,
            SOURCE__INSTR_SETTINGS: self._expected_environ,
        }
        expected = {
            phase_step.SETUP__VALIDATE_PRE_SDS: self._expected_environ,
            phase_step.ACT__VALIDATE_PRE_SDS: self._expected_environ,
            phase_step.BEFORE_ASSERT__VALIDATE_PRE_SDS: self._expected_environ,
            phase_step.ASSERT__VALIDATE_PRE_SDS: self._expected_environ,
            phase_step.CLEANUP__VALIDATE_PRE_SDS: self._expected_environ,
            phase_step.SETUP__MAIN: {
                SOURCE__INSTR_ENVIRONMENT: self._expected_environ,
                SOURCE__INSTR_SETTINGS: self._expected_environ,
                SOURCE__SETUP_SETTINGS: self._expected_environ,
            },
            phase_step.SETUP__VALIDATE_POST_SETUP: self._expected_environ,
            phase_step.ACT__VALIDATE_POST_SETUP: self._expected_environ,
            phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP: self._expected_environ,
            phase_step.ASSERT__VALIDATE_POST_SETUP: self._expected_environ,
            phase_step.ACT__PREPARE: self._expected_environ,
            phase_step.ACT__EXECUTE: {
                SOURCE__INSTR_ENVIRONMENT: self._expected_environ,
                SOURCE__ACT_EXE_INPUT: self._expected_environ,
            },
            phase_step.BEFORE_ASSERT__MAIN: non_setup_main_step,
            phase_step.ASSERT__MAIN: non_setup_main_step,
            phase_step.CLEANUP__MAIN: non_setup_main_step,
        }
        self.utc.assertEqual(expected,
                             self.recorder.phaseStep2recording,
                             'env vars per phase')

    def _assertions(self):
        self.__assert_test_sanity()
        self.__assert_expected_recorded_variables()

    def __assert_test_sanity(self):
        self.utc.assertEqual(self.full_result.status,
                             FullExeResultStatus.PASS,
                             'This test assumes that the Test Case is executed successfully: ' +
                             str(self.full_result.failure_info))


class _ActionWithPhaseStepAndRecording:
    def __init__(self,
                 recorder: instr_setup.Recorder,
                 my_phase_step: PhaseStep,
                 ):
        self.recorder = recorder
        self.my_phase_step = my_phase_step


class _ConfigurationPhaseActionThatSetsHdsCaseDirToParent:
    def __call__(self, configuration_builder: ConfigurationBuilder, *args):
        configuration_builder.set_hds_dir(RelHdsOptionType.REL_HDS_CASE,
                                          configuration_builder.get_hds_dir(RelHdsOptionType.REL_HDS_CASE).parent)


class _ConfigurationPhaseActionThatSetsHdsActDirToParentParent:
    def __call__(self, configuration_builder: ConfigurationBuilder, *args):
        configuration_builder.set_hds_dir(RelHdsOptionType.REL_HDS_ACT,
                                          configuration_builder.get_hds_dir(
                                              RelHdsOptionType.REL_HDS_ACT).parent.parent)


class _RecordEnvVars(_ActionWithPhaseStepAndRecording):
    def call(self, environment: InstructionEnvironmentForPreSdsStep, *args):
        self.recorder.set_phase_step_recording(self.my_phase_step,
                                               dict(environment.proc_exe_settings.environ))

    def non_setup_main(self,
                       environment: InstructionEnvironmentForPostSdsStep,
                       settings: InstructionSettings,
                       *args,
                       ):
        self.recorder.set_phase_step_recording(
            self.my_phase_step,
            {
                SOURCE__INSTR_ENVIRONMENT: mb_dict_of(environment.proc_exe_settings.environ),
                SOURCE__INSTR_SETTINGS: mb_dict_of(settings.environ()),
            }
        )

    def setup_main(self,
                   environment: InstructionEnvironmentForPostSdsStep,
                   settings: InstructionSettings,
                   os_services: OsServices,
                   settings_builder: SetupSettingsBuilder,
                   ):
        self.recorder.set_phase_step_recording(
            self.my_phase_step,
            {
                SOURCE__INSTR_ENVIRONMENT: mb_dict_of(environment.proc_exe_settings.environ),
                SOURCE__INSTR_SETTINGS: mb_dict_of(settings.environ()),
                SOURCE__SETUP_SETTINGS: mb_dict_of(settings_builder.environ),
            }
        )

    def as_execute_initial_action(self,
                                  environment: InstructionEnvironmentForPreSdsStep,
                                  atc_exe_input: AtcExecutionInput,
                                  output: StdOutputFiles):
        self.recorder.set_phase_step_recording(
            self.my_phase_step,
            {
                SOURCE__INSTR_ENVIRONMENT: mb_dict_of(environment.proc_exe_settings.environ),
                SOURCE__ACT_EXE_INPUT: mb_dict_of(atc_exe_input.environ),
            }
        )


def mb_dict_of(x: Optional[Mapping[str, str]]) -> Optional[Dict[str, str]]:
    return functional.map_optional(dict, x)


SOURCE__INSTR_ENVIRONMENT = 'instr-environment'
SOURCE__INSTR_SETTINGS = 'instr-settings'
SOURCE__SETUP_SETTINGS = 'setup-settings'
SOURCE__ACT_EXE_INPUT = 'act-exe-input'

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
