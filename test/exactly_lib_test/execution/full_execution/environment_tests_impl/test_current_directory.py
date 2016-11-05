import os
import unittest

from exactly_lib.execution.act_phase import new_eh_exit_code
from exactly_lib.execution.partial_execution import ActPhaseHandling
from exactly_lib.execution.phase_step_identifiers import phase_step
from exactly_lib.execution.phase_step_identifiers.phase_step import PhaseStep
from exactly_lib.execution.result import FullResultStatus
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.execution.full_execution.test_resources.test_case_base import FullExecutionTestCaseBase
from exactly_lib_test.execution.test_resources import recorder as instr_setup
from exactly_lib_test.execution.test_resources.act_source_executor import \
    ActSourceAndExecutorConstructorThatRunsConstantActions
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that, \
    before_assert_phase_instruction_that, assert_phase_instruction_that, \
    cleanup_phase_instruction_that, configuration_phase_instruction_that, act_phase_instruction_with_source
from exactly_lib_test.execution.test_resources.test_case_generation import full_test_case_with_instructions


def current_directory() -> str:
    return os.getcwd()


SUB_DIR_NAME = 'sub-dir'


class _ActionWithPhaseStepAndRecording:
    def __init__(self,
                 recorder: instr_setup.Recorder,
                 my_phase_step: PhaseStep):
        self.recorder = recorder
        self.my_phase_step = my_phase_step


class _RecordCurrDirThenMakeDirAndChangeToIt(_ActionWithPhaseStepAndRecording):
    def __call__(self, *args):
        self.recorder.set_phase_step_recording(self.my_phase_step, current_directory())
        os.mkdir(SUB_DIR_NAME)
        os.chdir(SUB_DIR_NAME)


class _RecordCurrDir(_ActionWithPhaseStepAndRecording):
    def __call__(self, *args):
        self.recorder.set_phase_step_recording(self.my_phase_step, current_directory())


class _RecordCurrDirAndReturn(_ActionWithPhaseStepAndRecording):
    def __init__(self,
                 recorder: instr_setup.Recorder,
                 my_phase_step: PhaseStep,
                 return_value):
        super().__init__(recorder, my_phase_step)
        self.return_value = return_value

    def __call__(self, *args):
        self.recorder.set_phase_step_recording(self.my_phase_step, current_directory())
        return self.return_value


class Test(FullExecutionTestCaseBase):
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False):
        self.recorder = instr_setup.Recorder()
        super().__init__(unittest_case,
                         dbg_do_not_delete_dir_structure)

    def _act_phase_handling(self) -> ActPhaseHandling:
        constructor = ActSourceAndExecutorConstructorThatRunsConstantActions(
            validate_post_setup_action=_RecordCurrDirAndReturn(self.recorder, phase_step.ACT__VALIDATE_POST_SETUP,
                                                               svh.new_svh_success()),
            execute_action=_RecordCurrDirAndReturn(self.recorder, phase_step.ACT__EXECUTE,
                                                   new_eh_exit_code(0)))
        return ActPhaseHandling(constructor)

    def _test_case(self) -> test_case_doc.TestCase:
        return full_test_case_with_instructions(
            [configuration_phase_instruction_that(
                main_initial_action=_RecordCurrDir(self.recorder,
                                                   phase_step.CONFIGURATION__MAIN))],
            [setup_phase_instruction_that(
                validate_post_setup_initial_action=_RecordCurrDir(self.recorder,
                                                                  phase_step.SETUP__VALIDATE_POST_SETUP),
                main_initial_action=_RecordCurrDirThenMakeDirAndChangeToIt(self.recorder,
                                                                           phase_step.SETUP__MAIN))],
            [act_phase_instruction_with_source(LineSequence(1, ('not used',)))],
            [before_assert_phase_instruction_that(
                validate_post_setup_initial_action=_RecordCurrDir(self.recorder,
                                                                  phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP),
                main_initial_action=_RecordCurrDirThenMakeDirAndChangeToIt(self.recorder,
                                                                           phase_step.BEFORE_ASSERT__MAIN))],
            [assert_phase_instruction_that(
                validate_post_setup_initial_action=_RecordCurrDir(self.recorder,
                                                                  phase_step.ASSERT__VALIDATE_POST_SETUP),
                main_initial_action=_RecordCurrDirThenMakeDirAndChangeToIt(self.recorder,
                                                                           phase_step.ASSERT__MAIN))],
            [cleanup_phase_instruction_that(
                main_initial_action=_RecordCurrDirThenMakeDirAndChangeToIt(self.recorder,
                                                                           phase_step.CLEANUP__MAIN))],
        )

    def _assertions(self):
        self.__assert_test_sanity()
        initial_dir = self.eds.act_dir
        initial_dir_recording = str(initial_dir)
        home_dir = str(self.initial_home_dir_path)
        expected_recordings = {
            phase_step.CONFIGURATION__MAIN:
                home_dir,
            phase_step.SETUP__MAIN:
                initial_dir_recording,
            phase_step.SETUP__VALIDATE_POST_SETUP:
                str(initial_dir / SUB_DIR_NAME),
            phase_step.ACT__VALIDATE_POST_SETUP:
                str(initial_dir / SUB_DIR_NAME),
            phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP:
                str(initial_dir / SUB_DIR_NAME),
            phase_step.ASSERT__VALIDATE_POST_SETUP:
                str(initial_dir / SUB_DIR_NAME),
            phase_step.ACT__EXECUTE:
                str(initial_dir / SUB_DIR_NAME),
            phase_step.BEFORE_ASSERT__MAIN:
                str(initial_dir / SUB_DIR_NAME),
            phase_step.ASSERT__MAIN:
                str(initial_dir / SUB_DIR_NAME / SUB_DIR_NAME),
            phase_step.CLEANUP__MAIN:
                str(initial_dir / SUB_DIR_NAME / SUB_DIR_NAME / SUB_DIR_NAME),
        }
        self.__assert_expected_internally_recorded_variables(expected_recordings)

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
