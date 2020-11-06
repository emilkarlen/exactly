import copy
import unittest
from typing import Dict, Optional

from exactly_lib.execution import phase_step
from exactly_lib.execution.full_execution.result import FullExeResultStatus
from exactly_lib.execution.phase_step import PhaseStep
from exactly_lib.tcfs.path_relativity import RelHdsOptionType
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.actor import Actor
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep
from exactly_lib.type_val_prims.string_model import StringModel
from exactly_lib.util.file_utils.std import StdOutputFiles
from exactly_lib_test.execution.full_execution.test_resources.test_case_base import FullExecutionTestCaseBase
from exactly_lib_test.execution.test_resources import recorder as instr_setup
from exactly_lib_test.execution.test_resources.instruction_test_resources import before_assert_phase_instruction_that, \
    assert_phase_instruction_that, cleanup_phase_instruction_that, \
    configuration_phase_instruction_that
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that
from exactly_lib_test.execution.test_resources.test_case_generation import full_test_case_with_instructions
from exactly_lib_test.test_case.actor.test_resources.actor_impls import ActorThatRunsConstantActions


class Test(FullExecutionTestCaseBase):
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False):
        self._expected_environ = {
            'MY_VAR': 'MY_VAR_VALUE'
        }
        super().__init__(unittest_case,
                         dbg_do_not_delete_dir_structure,
                         environ=copy.copy(self._expected_environ))
        self.recorder = instr_setup.Recorder()

    def _actor(self) -> Actor:
        return ActorThatRunsConstantActions(
            validate_pre_sds_initial_action=_RecordEnvVars(
                self.recorder,
                phase_step.ACT__VALIDATE_PRE_SDS),
            validate_post_setup_initial_action=_RecordEnvVars(
                self.recorder,
                phase_step.ACT__VALIDATE_POST_SETUP),
            prepare_initial_action=_RecordEnvVars(
                self.recorder,
                phase_step.ACT__PREPARE),
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
                                                               phase_step.SETUP__VALIDATE_PRE_SDS),
                validate_post_setup_initial_action=_RecordEnvVars(self.recorder,
                                                                  phase_step.SETUP__VALIDATE_POST_SETUP),
                main_initial_action=_RecordEnvVars(self.recorder,
                                                   phase_step.SETUP__MAIN))],
            [],
            [before_assert_phase_instruction_that(
                validate_pre_sds_initial_action=_RecordEnvVars(self.recorder,
                                                               phase_step.BEFORE_ASSERT__VALIDATE_PRE_SDS),
                validate_post_setup_initial_action=_RecordEnvVars(self.recorder,
                                                                  phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP),
                main_initial_action=_RecordEnvVars(self.recorder,
                                                   phase_step.BEFORE_ASSERT__MAIN))],
            [assert_phase_instruction_that(
                validate_pre_sds_initial_action=_RecordEnvVars(self.recorder,
                                                               phase_step.ASSERT__VALIDATE_PRE_SDS),
                validate_post_setup_initial_action=_RecordEnvVars(self.recorder,
                                                                  phase_step.ASSERT__VALIDATE_POST_SETUP),
                main_initial_action=_RecordEnvVars(self.recorder,
                                                   phase_step.ASSERT__MAIN))],
            [cleanup_phase_instruction_that(
                validate_pre_sds_initial_action=_RecordEnvVars(self.recorder,
                                                               phase_step.CLEANUP__VALIDATE_PRE_SDS),
                main_initial_action=_RecordEnvVars(self.recorder,
                                                   phase_step.CLEANUP__MAIN))],
        )

    def __assert_expected_recorded_variables(self, expected: Dict[PhaseStep, Dict[str, str]]):
        self._assert_expected_keys(expected,
                                   self.recorder.phaseStep2recording,
                                   'phase-step')
        for ph in expected.keys():
            self._assert_expected_keys(expected[ph],
                                       self.recorder.phaseStep2recording[ph],
                                       'Environment variables for phase-step ' + str(ph))
            self._assert_expected_values(expected[ph],
                                         self.recorder.phaseStep2recording[ph],
                                         'Environment variable value for phase-step ' + str(ph))

    def _assertions(self):
        self.__assert_test_sanity()
        expected_recorded_internally = {
            phase_step.SETUP__VALIDATE_PRE_SDS: self._expected_environ,
            phase_step.ACT__VALIDATE_PRE_SDS: self._expected_environ,
            phase_step.BEFORE_ASSERT__VALIDATE_PRE_SDS: self._expected_environ,
            phase_step.ASSERT__VALIDATE_PRE_SDS: self._expected_environ,
            phase_step.CLEANUP__VALIDATE_PRE_SDS: self._expected_environ,
            phase_step.SETUP__MAIN: self._expected_environ,
            phase_step.SETUP__VALIDATE_POST_SETUP: self._expected_environ,
            phase_step.ACT__VALIDATE_POST_SETUP: self._expected_environ,
            phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP: self._expected_environ,
            phase_step.ASSERT__VALIDATE_POST_SETUP: self._expected_environ,
            phase_step.ACT__PREPARE: self._expected_environ,
            phase_step.ACT__EXECUTE: self._expected_environ,
            phase_step.BEFORE_ASSERT__MAIN: self._expected_environ,
            phase_step.ASSERT__MAIN: self._expected_environ,
            phase_step.CLEANUP__MAIN: self._expected_environ,
        }
        self.__assert_expected_recorded_variables(expected_recorded_internally)

    def __assert_test_sanity(self):
        self.utc.assertEqual(self.full_result.status,
                             FullExeResultStatus.PASS,
                             'This test assumes that the Test Case is executed successfully: ' +
                             str(self.full_result.failure_info))

    def _assert_expected_keys(self,
                              expected: dict,
                              actual: dict,
                              key_entity: str):
        for e in expected.keys():
            self.utc.assertIn(e,
                              actual,
                              'Missing key for %s: %s' % (key_entity, str(e)))
        for a in actual.keys():
            self.utc.assertIn(a,
                              expected,
                              'Unexpected key for %s: %s' % (key_entity, str(a)))

    def _assert_expected_values(self,
                                expected: dict,
                                actual: dict,
                                key_entity: str):
        for k in expected:
            self.utc.assertEqual(expected[k],
                                 actual[k],
                                 'Value for %s %s' % (key_entity, str(k)))


class _ActionWithPhaseStepAndRecording:
    def __init__(self,
                 recorder: instr_setup.Recorder,
                 my_phase_step: PhaseStep):
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
    def __call__(self, environment: InstructionEnvironmentForPreSdsStep, *args, **kwargs):
        self.recorder.set_phase_step_recording(self.my_phase_step,
                                               copy.copy(environment.proc_exe_settings.environ))

    def as_execute_initial_action(self,
                                  environment: InstructionEnvironmentForPreSdsStep,
                                  stdin: Optional[StringModel],
                                  output: StdOutputFiles):
        self.recorder.set_phase_step_recording(self.my_phase_step,
                                               copy.copy(environment.proc_exe_settings.environ))
