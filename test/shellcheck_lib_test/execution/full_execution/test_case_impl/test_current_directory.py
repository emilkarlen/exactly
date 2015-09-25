import os
import pathlib
import unittest
import functools

from shellcheck_lib.test_case import test_case_doc
from shellcheck_lib.test_case.instruction import common
from shellcheck_lib.execution.phase_step import PhaseStep
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.test_case.instruction.sections.anonymous import ConfigurationBuilder
from shellcheck_lib_test.execution.full_execution.util.test_case_base import FullExecutionTestCaseBase
from shellcheck_lib.execution import phase_step
from shellcheck_lib_test.execution.util import instruction_that_record_and_return as instr_setup
from shellcheck_lib_test.execution.util.instruction_that_do_and_return import TestCaseGeneratorForTestCaseSetup, \
    print_to_file__generate_script
from shellcheck_lib_test.execution.util.py_unit_test_case_with_file_output import ModulesAndStatements
from shellcheck_lib_test.execution.util import python_code_gen


def current_directory() -> str:
    return os.getcwd()


def _set_home_dir_to_parent__anonymous_phase(recorder: instr_setup.Recorder,
                                             phase_step: PhaseStep,
                                             phase_environment: ConfigurationBuilder):
    pass


def _action__without_eds(recorder: instr_setup.Recorder,
                         phase_step: PhaseStep,
                         home_dir: pathlib.Path):
    pass


def _action__with_eds(recorder: instr_setup.Recorder,
                      phase_step: PhaseStep,
                      global_environment: common.GlobalEnvironmentForPostEdsPhase):
    recorder.set_phase_step_recording(phase_step, current_directory())
    os.chdir(str(global_environment.home_directory))


class Test(FullExecutionTestCaseBase):
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False):
        super().__init__(unittest_case,
                         dbg_do_not_delete_dir_structure)
        self.recorder = instr_setup.Recorder()

    def _test_case(self) -> test_case_doc.TestCase:
        setup = instr_setup.TestCaseSetupWithRecorder(
            validation_action__with_eds=_action__with_eds,
            execution_action__with_eds=_action__with_eds,
            execution__generate_script=script_for_print_current_directory_to_file,
        )
        plain_test_case_setup = setup.as_plain_test_case_setup(self.recorder)
        return TestCaseGeneratorForTestCaseSetup(plain_test_case_setup).test_case

    def _assertions(self):
        self.__assert_test_sanity()
        for_post_eds = str(self.eds.test_root_dir)
        expected_recorded_internally = {
            phase_step.SETUP_EXECUTE: for_post_eds,
            phase_step.ACT_VALIDATE: for_post_eds,
            phase_step.ACT_SCRIPT_GENERATION: for_post_eds,
            phase_step.ASSERT_VALIDATE: for_post_eds,
            phase_step.ASSERT_EXECUTE: for_post_eds,
            phase_step.CLEANUP_EXECUTE: for_post_eds,
        }
        expected_act_output = for_post_eds + os.linesep
        self.__assert_expected_internally_recorded_variables(expected_recorded_internally)
        self.__assert_expected_act_script_execution_recorded_variables(expected_act_output)

    def __assert_test_sanity(self):
        self.utc.assertEqual(self.full_result.status,
                             FullResultStatus.PASS,
                             'This test assumes that the Test Case is executed successfully.')

    def __assert_expected_internally_recorded_variables(self, expected):
        self._assert_expected_keys(expected,
                                   self.recorder.phaseStep2recording,
                                   'phase-step')

        self._assert_expected_values(expected,
                                     self.recorder.phaseStep2recording,
                                     'Current Directory')

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


def python_code_for_print_current_directory(file_variable: str) -> ModulesAndStatements:
    statement = python_code_gen.print_value('os.getcwd()', file_variable)
    code = [statement]
    return ModulesAndStatements({'os'},
                                code)


script_for_print_current_directory_to_file = functools.partial(print_to_file__generate_script,
                                                               python_code_for_print_current_directory,
                                                               ACT_SCRIPT_OUTPUT_FILE_NAME)
