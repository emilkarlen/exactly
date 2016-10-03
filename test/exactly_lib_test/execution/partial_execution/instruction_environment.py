import functools
import unittest

from exactly_lib.execution import partial_execution as sut
from exactly_lib.execution import phases
from exactly_lib.execution.execution_directory_structure import eds_log_phase_dir
from exactly_lib.execution.phases import PhaseEnum
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.execution.partial_execution.test_resources.basic import test, \
    TestCaseWithCommonDefaultInstructions, Result, dummy_act_phase_handling
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that, \
    act_phase_instruction_with, before_assert_phase_instruction_that, assert_phase_instruction_that, \
    cleanup_phase_instruction_that
from exactly_lib_test.execution.test_resources.test_case_generation import partial_test_case_with_instructions


class Test(unittest.TestCase):
    def test_log_dirs(self):
        recorder = {}
        test_case = partial_test_case_with_instructions(
            [setup_phase_instruction_that(main_initial_action=RecordLogDirForPhase(PhaseEnum.SETUP, recorder))],
            [act_phase_instruction_with(LineSequence(1, ('line',)))],
            [before_assert_phase_instruction_that(main_initial_action=RecordLogDirForPhase(PhaseEnum.BEFORE_ASSERT,
                                                                                           recorder))],
            [assert_phase_instruction_that(main_initial_action=RecordLogDirForPhase(PhaseEnum.ASSERT, recorder))],
            [cleanup_phase_instruction_that(main_initial_action=RecordLogDirForPhase(PhaseEnum.CLEANUP, recorder))],
        )
        test(
            self,
            test_case,
            functools.partial(log_dir_is_correct_for_each_phase, recorder),
            dummy_act_phase_handling(),
            is_keep_execution_directory_root=False)


def log_dir_is_correct_for_each_phase(recordings: dict,
                                      put: unittest.TestCase,
                                      actual: Result):
    put.assertFalse(actual.partial_result.is_failure)
    eds = actual.execution_directory_structure
    expected = {
        PhaseEnum.SETUP: eds_log_phase_dir(eds, phases.SETUP.identifier),
        # PhaseEnum.ACT: eds_log_phase_dir(eds, phases.ACT.identifier),
        PhaseEnum.BEFORE_ASSERT: eds_log_phase_dir(eds, phases.BEFORE_ASSERT.identifier),
        PhaseEnum.ASSERT: eds_log_phase_dir(eds, phases.ASSERT.identifier),
        PhaseEnum.CLEANUP: eds_log_phase_dir(eds, phases.CLEANUP.identifier),
    }
    put.assertDictEqual(expected,
                        recordings,
                        'Log directory per phase')


def test_case_that_does_nothing() -> sut.TestCase:
    return TestCaseWithCommonDefaultInstructions().test_case


class RecordLogDirForPhase:
    def __init__(self, phase: PhaseEnum, recorder: dict):
        self.phase = phase
        self.recorder = recorder

    def __call__(self, environment: GlobalEnvironmentForPostEdsPhase, *args):
        self.recorder[self.phase] = environment.phase_logging.dir_path


def suite() -> unittest.makeSuite:
    return unittest.makeSuite(Test)


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
