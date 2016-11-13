import os
import pathlib
import types
import unittest

from exactly_lib.execution import environment_variables
from exactly_lib.execution.phase_step_identifiers import phase_step
from exactly_lib.execution.phase_step_identifiers.phase_step import PhaseStep
from exactly_lib.execution.result import FullResultStatus
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib_test.execution.full_execution.test_resources.test_case_base import FullExecutionTestCaseBase
from exactly_lib_test.execution.test_resources import python_code_gen as py
from exactly_lib_test.execution.test_resources import recorder as instr_setup
from exactly_lib_test.execution.test_resources.act_source_executor import \
    ActSourceAndExecutorConstructorThatRunsConstantActions
from exactly_lib_test.execution.test_resources.instruction_test_resources import before_assert_phase_instruction_that, \
    assert_phase_instruction_that, cleanup_phase_instruction_that, \
    configuration_phase_instruction_that
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that
from exactly_lib_test.execution.test_resources.test_case_generation import full_test_case_with_instructions


class Test(FullExecutionTestCaseBase):
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False):
        super().__init__(unittest_case,
                         dbg_do_not_delete_dir_structure)
        self.recorder = instr_setup.Recorder()

    def _act_phase_handling(self) -> ActPhaseHandling:
        executor_constructor = ActSourceAndExecutorConstructorThatRunsConstantActions(
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
                phase_step.ACT__EXECUTE))
        return ActPhaseHandling(executor_constructor)

    def _test_case(self) -> test_case_doc.TestCase:
        return full_test_case_with_instructions(
            [configuration_phase_instruction_that(
                main_initial_action=_ConfigurationPhaseActionThatSetsHomeDirToParent())],
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

    def __assert_expected_recorded_variables(self, expected):
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
        home_dir_after_configuration = str(self.initial_home_dir_path.parent)
        for_pre_sds = {
            environment_variables.ENV_VAR_HOME: home_dir_after_configuration
        }
        set_at_sds_creation = {
            environment_variables.ENV_VAR_HOME: home_dir_after_configuration,
            environment_variables.ENV_VAR_ACT: str(self.sds.act_dir),
            environment_variables.ENV_VAR_TMP: str(self.sds.tmp.user_dir),
        }
        set_after_act = {
            environment_variables.ENV_VAR_HOME: home_dir_after_configuration,
            environment_variables.ENV_VAR_ACT: str(self.sds.act_dir),
            environment_variables.ENV_VAR_TMP: str(self.sds.tmp.user_dir),
            environment_variables.ENV_VAR_RESULT: str(self.sds.result.root_dir),
        }
        expected_recorded_internally = {
            phase_step.SETUP__VALIDATE_PRE_SDS: for_pre_sds,
            phase_step.ACT__VALIDATE_PRE_SDS: for_pre_sds,
            phase_step.BEFORE_ASSERT__VALIDATE_PRE_SDS: for_pre_sds,
            phase_step.ASSERT__VALIDATE_PRE_SDS: for_pre_sds,
            phase_step.CLEANUP__VALIDATE_PRE_SDS: for_pre_sds,
            phase_step.SETUP__MAIN: set_at_sds_creation,
            phase_step.SETUP__VALIDATE_POST_SETUP: set_at_sds_creation,
            phase_step.ACT__VALIDATE_POST_SETUP: set_at_sds_creation,
            phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP: set_at_sds_creation,
            phase_step.ASSERT__VALIDATE_POST_SETUP: set_at_sds_creation,
            phase_step.ACT__PREPARE: set_at_sds_creation,
            phase_step.ACT__EXECUTE: set_at_sds_creation,
            phase_step.BEFORE_ASSERT__MAIN: set_after_act,
            phase_step.ASSERT__MAIN: set_after_act,
            phase_step.CLEANUP__MAIN: set_after_act,
        }
        expected_act_output = ''.join([
            '%s=%s%s' % (
                environment_variables.ENV_VAR_HOME, home_dir_after_configuration, os.linesep),
            '%s=%s%s' % (
                environment_variables.ENV_VAR_ACT, str(self.sds.act_dir), os.linesep),
            '%s=%s%s' % (environment_variables.ENV_VAR_TMP, str(self.sds.tmp.user_dir),
                         os.linesep),
        ])
        self.__assert_expected_recorded_variables(expected_recorded_internally)

    def __assert_test_sanity(self):
        self.utc.assertEqual(self.full_result.status,
                             FullResultStatus.PASS,
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


class _ConfigurationPhaseActionThatSetsHomeDirToParent:
    def __call__(self, phase_environment: ConfigurationBuilder, *args):
        phase_environment.set_home_dir(phase_environment.home_dir_path.parent)


class _RecordEnvVars(_ActionWithPhaseStepAndRecording):
    def __call__(self, environment: InstructionEnvironmentForPreSdsStep, *args, **kwargs):
        self.recorder.set_phase_step_recording(self.my_phase_step, env_vars_dict(environment))


def env_vars_dict(environment: InstructionEnvironmentForPreSdsStep) -> dict:
    ret_val = dict()
    for env_var in environment_variables.ALL_ENV_VARS:
        if env_var in environment.environ:
            ret_val[env_var] = environment.environ[env_var]
    return ret_val


def print_to_file__generate_script(code_using_file_opened_for_writing: types.FunctionType,
                                   file_name: str) -> list:
    """
    Function that is designed as the execution__generate_script argument to TestCaseSetup, after
    giving the first two arguments using partial application.

    :param code_using_file_opened_for_writing: function: file_variable: str -> ModulesAndStatements
    :param file_name: the name of the file to output to.
    """
    file_path = pathlib.Path() / file_name
    file_name = str(file_path)
    file_var = '_file_var'
    mas = code_using_file_opened_for_writing(file_var)
    all_statements = py.with_opened_file(file_name,
                                         file_var,
                                         'w',
                                         mas.statements)

    return py.program_lines(mas.used_modules,
                            all_statements)
