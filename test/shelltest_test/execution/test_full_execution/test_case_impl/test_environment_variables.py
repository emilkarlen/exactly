import os
import pathlib
import unittest
import functools

from shelltest.test_case import abs_syn_gen
from shelltest.test_case import instructions
from shelltest.execution.phase_step import PhaseStep
from shelltest.execution.result import FullResultStatus
from shelltest_test.execution.test_full_execution.util.test_case_base import FullExecutionTestCaseBase
from shelltest.execution import phase_step
from shelltest_test.execution.util import instruction_that_record_and_return as instr_setup
from shelltest_test.execution.util.instruction_that_do_and_return import TestCaseGeneratorForTestCaseSetup, \
    print_to_file__generate_script
from shelltest_test.execution.util.py_unit_test_case_with_file_output import ModulesAndStatements
from shelltest_test.execution.util.python_code_gen import print_env_var_if_defined


def env_vars_dict() -> dict:
    ret_val = dict()
    for env_var in instructions.ALL_ENV_VARS:
        if env_var in os.environ:
            ret_val[env_var] = os.environ[env_var]
    return ret_val


def _set_home_dir_to_parent__anonymous_phase(recorder: instr_setup.Recorder,
                                             phase_step: PhaseStep,
                                             phase_environment: instructions.PhaseEnvironmentForAnonymousPhase):
    recorder.set_phase_step_recording(phase_step, env_vars_dict())
    phase_environment.set_home_dir(phase_environment.home_dir_path.parent)


def _action__without_eds(recorder: instr_setup.Recorder,
                         phase_step: PhaseStep,
                         home_dir: pathlib.Path):
    recorder.set_phase_step_recording(phase_step, env_vars_dict())


def _action__with_eds(recorder: instr_setup.Recorder,
                      phase_step: PhaseStep,
                      global_environment: instructions.GlobalEnvironmentForNamedPhase):
    recorder.set_phase_step_recording(phase_step, env_vars_dict())


class Test(FullExecutionTestCaseBase):
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False):
        super().__init__(unittest_case,
                         dbg_do_not_delete_dir_structure)
        self.recorder = instr_setup.Recorder()

    def _test_case(self) -> abs_syn_gen.TestCase:
        setup = instr_setup.TestCaseSetupWithRecorder(
            validation_action__without_eds=_action__without_eds,
            anonymous_phase_action=_set_home_dir_to_parent__anonymous_phase,
            validation_action__with_eds=_action__with_eds,
            execution_action__with_eds=_action__with_eds,
            execution__generate_script=script_for_print_environment_variables_to_file,
        )
        plain_test_case_setup = setup.as_plain_test_case_setup(self.recorder)
        return TestCaseGeneratorForTestCaseSetup(plain_test_case_setup).test_case

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
        for_anonymous_phase = dict()
        home_dir_after_anonymous = str(self.initial_home_dir_path.parent)
        for_pre_eds = {instructions.ENV_VAR_HOME: home_dir_after_anonymous}
        for_post_eds = {
            instructions.ENV_VAR_HOME: home_dir_after_anonymous,
            instructions.ENV_VAR_TEST: str(self.eds.test_root_dir),
            instructions.ENV_VAR_TMP: str(self.eds.tmp_dir),
        }
        expected_recorded_internally = {
            phase_step.ANONYMOUS_EXECUTE: for_anonymous_phase,
            phase_step.SETUP_VALIDATE: for_pre_eds,
            phase_step.SETUP_EXECUTE: for_post_eds,
            phase_step.ACT_VALIDATE: for_post_eds,
            phase_step.ACT_SCRIPT_GENERATION: for_post_eds,
            phase_step.ASSERT_VALIDATE: for_post_eds,
            phase_step.ASSERT_EXECUTE: for_post_eds,
            phase_step.CLEANUP_EXECUTE: for_post_eds,
        }
        expected_act_output = ''.join([
            '%s=%s%s' % (instructions.ENV_VAR_HOME, home_dir_after_anonymous, os.linesep),
            '%s=%s%s' % (instructions.ENV_VAR_TEST, str(self.eds.test_root_dir), os.linesep),
            '%s=%s%s' % (instructions.ENV_VAR_TMP, str(self.eds.tmp_dir), os.linesep),
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
            self.utc.assertTrue(e in actual,
                                'Missing key for %s: %s' % (key_entity, str(e)))
        for a in actual.keys():
            self.utc.assertTrue(a in expected,
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
            self.full_result.execution_directory_structure.test_root_dir / ACT_SCRIPT_OUTPUT_FILE_NAME,
            expected_act_output,
            'Envronment Variables printed from act/script execution')


ACT_SCRIPT_OUTPUT_FILE_NAME = 'act-script-output.txt'


def python_code_for_print_environment_variables(file_variable: str) -> ModulesAndStatements:
    code = []
    for env_var in instructions.ALL_ENV_VARS:
        code.extend(print_env_var_if_defined(env_var, file_variable))
    return ModulesAndStatements({'os'},
                                code)


script_for_print_environment_variables_to_file = functools.partial(print_to_file__generate_script,
                                                                   python_code_for_print_environment_variables,
                                                                   ACT_SCRIPT_OUTPUT_FILE_NAME)
