import functools
import unittest

from shellcheck_lib.execution import partial_execution as sut
from shellcheck_lib.execution import phases
from shellcheck_lib.execution.execution_directory_structure import log_phase_dir
from shellcheck_lib.execution.phases import PhaseEnum
from shellcheck_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.phases.result import pfh
from shellcheck_lib.test_case.phases.result import sh
from shellcheck_lib.test_case.phases.result import svh
from shellcheck_lib_test.execution.partial_execution.test_resources.basic import py3_test, \
    TestCaseWithCommonDefaultInstructions, Result


class Test(unittest.TestCase):
    def test_log_dirs(self):
        recorder = {}
        test_case = TestCaseThatRecordsLogDirPerPhase(recorder).test_case
        py3_test(
                self,
                test_case,
                functools.partial(log_dir_is_correct_for_each_phase, recorder),
                is_keep_execution_directory_root=False)


def log_dir_is_correct_for_each_phase(recordings: dict,
                                      put: unittest.TestCase,
                                      actual: Result):
    put.assertFalse(actual.partial_result.is_failure)
    eds = actual.execution_directory_structure
    expected = {
        PhaseEnum.SETUP: log_phase_dir(eds, phases.SETUP.identifier),
        PhaseEnum.ACT: log_phase_dir(eds, phases.ACT.identifier),
        PhaseEnum.BEFORE_ASSERT: log_phase_dir(eds, phases.BEFORE_ASSERT.identifier),
        PhaseEnum.ASSERT: log_phase_dir(eds, phases.ASSERT.identifier),
        PhaseEnum.CLEANUP: log_phase_dir(eds, phases.CLEANUP.identifier),
    }
    put.assertDictEqual(expected,
                        recordings,
                        'Log directory per phase')


def test_case_that_does_nothing() -> sut.TestCase:
    return TestCaseWithCommonDefaultInstructions().test_case


class TestCaseThatRecordsLogDirPerPhase(TestCaseWithCommonDefaultInstructions):
    def __init__(self, recorder: dict):
        super().__init__()
        self.recorder = recorder

    def _default_instructions(self, phase: PhaseEnum) -> list:
        return [
            functools.partial(self._recording_function, phase)
        ]

    def _recording_function(self, phase: PhaseEnum, environment: GlobalEnvironmentForPostEdsPhase, *args):
        self.recorder[phase] = environment.phase_logging.dir_path
        if phase == PhaseEnum.ACT:
            return sh.new_sh_success()
        if phase == PhaseEnum.ASSERT:
            return pfh.new_pfh_pass()
        return svh.new_svh_success()


def suite() -> unittest.makeSuite:
    return unittest.makeSuite(Test)


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
