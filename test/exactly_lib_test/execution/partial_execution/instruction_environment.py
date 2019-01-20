import unittest

import functools

from exactly_lib.execution.partial_execution.configuration import TestCase
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phase_identifier import PhaseEnum
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_file_structure.sandbox_directory_structure import sds_log_phase_dir
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.execution.partial_execution.test_resources.basic import test, \
    TestCaseWithCommonDefaultInstructions, Result
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that, \
    before_assert_phase_instruction_that, assert_phase_instruction_that, \
    cleanup_phase_instruction_that, act_phase_instruction_with_source
from exactly_lib_test.execution.test_resources.test_case_generation import partial_test_case_with_instructions
from exactly_lib_test.test_case.act_phase_handling.test_resources.act_phase_handlings import dummy_actor


def suite() -> unittest.makeSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_instruction_environment_specifies_correct_log_dir_for_each_phase(self):
        recorder = {}
        test_case = partial_test_case_with_instructions(
            [setup_phase_instruction_that(main_initial_action=RecordLogDirForPhase(PhaseEnum.SETUP, recorder))],
            [act_phase_instruction_with_source(LineSequence(1, ('line',)))],
            [before_assert_phase_instruction_that(main_initial_action=RecordLogDirForPhase(PhaseEnum.BEFORE_ASSERT,
                                                                                           recorder))],
            [assert_phase_instruction_that(main_initial_action=RecordLogDirForPhase(PhaseEnum.ASSERT, recorder))],
            [cleanup_phase_instruction_that(main_initial_action=RecordLogDirForPhase(PhaseEnum.CLEANUP, recorder))],
        )
        test(
            self,
            test_case,
            dummy_actor(),
            functools.partial(log_dir_is_correct_for_each_phase, recorder),
            is_keep_sandbox=False)


def log_dir_is_correct_for_each_phase(recordings: dict,
                                      put: unittest.TestCase,
                                      actual: Result):
    put.assertFalse(actual.partial_result.is_failure)
    sds = actual.sds
    expected = {
        PhaseEnum.SETUP: sds_log_phase_dir(sds, phase_identifier.SETUP.identifier),
        PhaseEnum.BEFORE_ASSERT: sds_log_phase_dir(sds, phase_identifier.BEFORE_ASSERT.identifier),
        PhaseEnum.ASSERT: sds_log_phase_dir(sds, phase_identifier.ASSERT.identifier),
        PhaseEnum.CLEANUP: sds_log_phase_dir(sds, phase_identifier.CLEANUP.identifier),
    }
    put.assertDictEqual(expected,
                        recordings,
                        'Log directory per phase')


def test_case_that_does_nothing() -> TestCase:
    return TestCaseWithCommonDefaultInstructions().test_case


class RecordLogDirForPhase:
    def __init__(self, phase: PhaseEnum, recorder: dict):
        self.phase = phase
        self.recorder = recorder

    def __call__(self, environment: InstructionEnvironmentForPostSdsStep, *args):
        self.recorder[self.phase] = environment.phase_logging.dir_path


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
