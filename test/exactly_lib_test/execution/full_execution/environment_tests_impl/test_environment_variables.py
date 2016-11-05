import os
import pathlib
import types
import unittest

from exactly_lib.act_phase_setups.script_interpretation import python3
from exactly_lib.execution import environment_variables
from exactly_lib.execution.act_phase import ActPhaseHandling
from exactly_lib.execution.phase_step_identifiers import phase_step
from exactly_lib.execution.phase_step_identifiers.phase_step import PhaseStep
from exactly_lib.execution.result import FullResultStatus
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.execution.full_execution.test_resources.test_case_base import FullExecutionTestCaseBase
from exactly_lib_test.execution.test_resources import python_code_gen as py
from exactly_lib_test.execution.test_resources import recorder as instr_setup
from exactly_lib_test.execution.test_resources.execution_recording.act_program_executor import \
    ActSourceAndExecutorConstructorWithActionsForExecutor
from exactly_lib_test.execution.test_resources.instruction_test_resources import before_assert_phase_instruction_that, \
    assert_phase_instruction_that, cleanup_phase_instruction_that, \
    act_phase_instruction_with_source
from exactly_lib_test.execution.test_resources.instruction_test_resources import configuration_phase_instruction_that
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that
from exactly_lib_test.execution.test_resources.py_unit_test_case_with_file_output import ModulesAndStatements
from exactly_lib_test.execution.test_resources.python_code_gen import print_env_var_if_defined
from exactly_lib_test.execution.test_resources.test_case_generation import full_test_case_with_instructions


class Test(FullExecutionTestCaseBase):
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False):
        super().__init__(unittest_case,
                         dbg_do_not_delete_dir_structure)
        self.recorder = instr_setup.Recorder()

    def _act_phase_handling(self) -> ActPhaseHandling:
        executor_constructor = ActSourceAndExecutorConstructorWithActionsForExecutor(
            python3.new_act_phase_setup().source_and_executor_constructor,
            before_wrapped_validate_pre_eds=_RecordEnvVars(
                self.recorder,
                phase_step.ACT__VALIDATE_PRE_EDS),
            before_wrapped_validate_post_setup=_RecordEnvVars(
                self.recorder,
                phase_step.ACT__VALIDATE_POST_SETUP),
            before_wrapped_prepare=_RecordEnvVars(
                self.recorder,
                phase_step.ACT__PREPARE),
            before_wrapped_execute=_RecordEnvVars(
                self.recorder,
                phase_step.ACT__EXECUTE))
        return ActPhaseHandling(executor_constructor)

    def _test_case(self) -> test_case_doc.TestCase:
        py_pgm_to_print_env_vars = print_to_file__generate_script(python_code_for_print_environment_variables,
                                                                  ACT_SCRIPT_OUTPUT_FILE_NAME)
        return full_test_case_with_instructions(
            [configuration_phase_instruction_that(
                main_initial_action=_ConfigurationPhaseActionThatRecordsEnvVarsAndSetsHomeDirToParent(self.recorder,
                                                                                                      phase_step.CONFIGURATION__MAIN))],
            [setup_phase_instruction_that(
                validate_pre_eds_initial_action=_RecordEnvVars(self.recorder,
                                                               phase_step.SETUP__VALIDATE_PRE_EDS),
                validate_post_setup_initial_action=_RecordEnvVars(self.recorder,
                                                                  phase_step.SETUP__VALIDATE_POST_SETUP),
                main_initial_action=_RecordEnvVars(self.recorder,
                                                   phase_step.SETUP__MAIN))],
            [act_phase_instruction_with_source(LineSequence(72, py_pgm_to_print_env_vars))],
            [before_assert_phase_instruction_that(
                validate_pre_eds_initial_action=_RecordEnvVars(self.recorder,
                                                               phase_step.BEFORE_ASSERT__VALIDATE_PRE_EDS),
                validate_post_setup_initial_action=_RecordEnvVars(self.recorder,
                                                                  phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP),
                main_initial_action=_RecordEnvVars(self.recorder,
                                                   phase_step.BEFORE_ASSERT__MAIN))],
            [assert_phase_instruction_that(
                validate_pre_eds_initial_action=_RecordEnvVars(self.recorder,
                                                               phase_step.ASSERT__VALIDATE_PRE_EDS),
                validate_post_setup_initial_action=_RecordEnvVars(self.recorder,
                                                                  phase_step.ASSERT__VALIDATE_POST_SETUP),
                main_initial_action=_RecordEnvVars(self.recorder,
                                                   phase_step.ASSERT__MAIN))],
            [cleanup_phase_instruction_that(
                validate_pre_eds_initial_action=_RecordEnvVars(self.recorder,
                                                               phase_step.CLEANUP__VALIDATE_PRE_EDS),
                main_initial_action=_RecordEnvVars(self.recorder,
                                                   phase_step.CLEANUP__MAIN))],
        )

    def __assert_expected_internally_recorded_variables(self, expected):
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
        for_configuration_phase = {}
        home_dir_after_configuration = str(self.initial_home_dir_path.parent)
        for_pre_eds = {
            environment_variables.ENV_VAR_HOME: home_dir_after_configuration
        }
        set_at_eds_creation = {
            environment_variables.ENV_VAR_HOME: home_dir_after_configuration,
            environment_variables.ENV_VAR_ACT: str(self.eds.act_dir),
            environment_variables.ENV_VAR_TMP: str(self.eds.tmp.user_dir),
        }
        set_after_act = {
            environment_variables.ENV_VAR_HOME: home_dir_after_configuration,
            environment_variables.ENV_VAR_ACT: str(self.eds.act_dir),
            environment_variables.ENV_VAR_TMP: str(self.eds.tmp.user_dir),
            environment_variables.ENV_VAR_RESULT: str(self.eds.result.root_dir),
        }
        expected_recorded_internally = {
            phase_step.CONFIGURATION__MAIN: for_configuration_phase,
            phase_step.SETUP__VALIDATE_PRE_EDS: for_pre_eds,
            phase_step.ACT__VALIDATE_PRE_EDS: for_pre_eds,
            phase_step.BEFORE_ASSERT__VALIDATE_PRE_EDS: for_pre_eds,
            phase_step.ASSERT__VALIDATE_PRE_EDS: for_pre_eds,
            phase_step.CLEANUP__VALIDATE_PRE_EDS: for_pre_eds,
            phase_step.SETUP__MAIN: set_at_eds_creation,
            phase_step.SETUP__VALIDATE_POST_SETUP: set_at_eds_creation,
            phase_step.ACT__VALIDATE_POST_SETUP: set_at_eds_creation,
            phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP: set_at_eds_creation,
            phase_step.ASSERT__VALIDATE_POST_SETUP: set_at_eds_creation,
            phase_step.ACT__PREPARE: set_at_eds_creation,
            phase_step.ACT__EXECUTE: set_at_eds_creation,
            phase_step.BEFORE_ASSERT__MAIN: set_after_act,
            phase_step.ASSERT__MAIN: set_after_act,
            phase_step.CLEANUP__MAIN: set_after_act,
        }
        expected_act_output = ''.join([
            '%s=%s%s' % (
                environment_variables.ENV_VAR_HOME, home_dir_after_configuration, os.linesep),
            '%s=%s%s' % (
                environment_variables.ENV_VAR_ACT, str(self.eds.act_dir), os.linesep),
            '%s=%s%s' % (environment_variables.ENV_VAR_TMP, str(self.eds.tmp.user_dir),
                         os.linesep),
        ])
        self.__assert_expected_internally_recorded_variables(expected_recorded_internally)
        self.__assert_expected_act_script_execution_recorded_variables(expected_act_output)

    def __assert_test_sanity(self):
        self.utc.assertEqual(self.full_result.status,
                             FullResultStatus.PASS,
                             'This test assumes that the Test Case is executed successfully.')

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

    def __assert_expected_act_script_execution_recorded_variables(self, expected_act_output: str):
        self.assert_is_regular_file_with_contents(
            self.full_result.execution_directory_structure.act_dir / ACT_SCRIPT_OUTPUT_FILE_NAME,
            expected_act_output,
            'Environment Variables printed from act/script execution')


ACT_SCRIPT_OUTPUT_FILE_NAME = 'act-script-output.txt'


def python_code_for_print_environment_variables(file_variable: str) -> ModulesAndStatements:
    code = []
    for env_var in environment_variables.ALL_ENV_VARS:
        code.extend(print_env_var_if_defined(env_var, file_variable))
    return ModulesAndStatements({'os'},
                                code)


class _ActionWithPhaseStepAndRecording:
    def __init__(self,
                 recorder: instr_setup.Recorder,
                 my_phase_step: PhaseStep):
        self.recorder = recorder
        self.my_phase_step = my_phase_step


class _ConfigurationPhaseActionThatRecordsEnvVarsAndSetsHomeDirToParent(_ActionWithPhaseStepAndRecording):
    def __call__(self, phase_environment: ConfigurationBuilder, *args):
        self.recorder.set_phase_step_recording(self.my_phase_step, env_vars_dict())
        phase_environment.set_home_dir(phase_environment.home_dir_path.parent)


class _RecordEnvVars(_ActionWithPhaseStepAndRecording):
    def __call__(self, *args, **kwargs):
        self.recorder.set_phase_step_recording(self.my_phase_step, env_vars_dict())


def env_vars_dict() -> dict:
    ret_val = dict()
    for env_var in environment_variables.ALL_ENV_VARS:
        if env_var in os.environ:
            ret_val[env_var] = os.environ[env_var]
    return ret_val


def print_to_file__generate_script(code_using_file_opened_for_writing: types.FunctionType,
                                   file_name: str):
    """
    Function that is designed as the execution__generate_script argument to TestCaseSetup, after
    giving the first two arguments using partial application.

    :param code_using_file_opened_for_writing: function: file_variable: str -> ModulesAndStatements
    :param file_name: the name of the file to output to.
    :param global_environment: Environment from act instruction
    :param phase_environment: Environment from act instruction
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
