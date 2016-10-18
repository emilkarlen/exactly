import pathlib
import unittest

from exactly_lib import program_info
from exactly_lib.execution import partial_execution as sut
from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.execution.act_phase import ActSourceAndExecutor, ExitCodeOrHardError, new_eh_exit_code, \
    ActPhaseHandling
from exactly_lib.section_document.model import new_empty_section_contents
from exactly_lib.test_case.phases.common import HomeAndEds
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.std import StdFiles
from exactly_lib_test.execution.test_resources.execution_recording.act_program_executor import \
    ActSourceAndExecutorConstructorForConstantExecutor


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestCurrentDirectory),
        unittest.makeSuite(TestExecute),
    ])


class TestCurrentDirectory(unittest.TestCase):
    def runTest(self):
        # ARRANGE
        executor_that_records_current_dir = _ExecutorThatRecordsCurrentDir()
        home_dir_path = pathlib.Path().resolve()
        # ACT #
        sut.execute(
            ActPhaseHandling(ActSourceAndExecutorConstructorForConstantExecutor(executor_that_records_current_dir)),
            _empty_test_case(),
            home_dir_path,
            program_info.PROGRAM_NAME + '-test-',
            False)
        # ASSERT #
        phase_step_2_cwd = executor_that_records_current_dir.phase_step_2_cwd
        home_and_eds = executor_that_records_current_dir.actual_home_and_eds
        eds = home_and_eds.eds
        self.assertEqual(len(phase_step_2_cwd),
                         4,
                         'Expects recordings for 4 steps')
        self.assertEqual(phase_step_2_cwd[phase_step.ACT__VALIDATE_PRE_EDS],
                         str(home_and_eds.home_dir_path),
                         'Current dir for ' + str(phase_step.ACT__VALIDATE_PRE_EDS))
        self.assertEqual(phase_step_2_cwd[phase_step.ACT__VALIDATE_POST_SETUP],
                         str(eds.act_dir),
                         'Current dir for ' + str(phase_step.ACT__VALIDATE_POST_SETUP))
        self.assertEqual(phase_step_2_cwd[phase_step.ACT__PREPARE],
                         str(eds.act_dir),
                         'Current dir for ' + str(phase_step.ACT__PREPARE))
        self.assertEqual(phase_step_2_cwd[phase_step.ACT__EXECUTE],
                         str(eds.act_dir),
                         'Current dir for ' + str(phase_step.ACT__EXECUTE))


class TestExecute(unittest.TestCase):
    def test_exitcode_should_be_saved_in_file(self):
        self.fail('not impl')

    def test_stdout_should_be_saved_in_file(self):
        self.fail('not impl')

    def test_stdin_should_be_available(self):
        self.fail('not impl')


class _ExecutorThatRecordsCurrentDir(ActSourceAndExecutor):
    def __init__(self):
        self._home_and_eds = None
        self.phase_step_2_cwd = {}

    def validate_pre_eds(self, home_dir_path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        self._register_cwd_for(phase_step.ACT__VALIDATE_PRE_EDS)
        return svh.new_svh_success()

    def validate_post_setup(self, home_and_eds: HomeAndEds) -> svh.SuccessOrValidationErrorOrHardError:
        self._home_and_eds = home_and_eds
        self._register_cwd_for(phase_step.ACT__VALIDATE_POST_SETUP)
        return svh.new_svh_success()

    def prepare(self, home_and_eds: HomeAndEds, script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        self._register_cwd_for(phase_step.ACT__PREPARE)
        return sh.new_sh_success()

    def execute(self, home_and_eds: HomeAndEds, script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        self._register_cwd_for(phase_step.ACT__EXECUTE)
        return new_eh_exit_code(0)

    def _register_cwd_for(self, step):
        self.phase_step_2_cwd[step] = str(pathlib.Path().resolve())

    @property
    def actual_home_and_eds(self) -> HomeAndEds:
        return self._home_and_eds


def _empty_test_case() -> sut.TestCase:
    return sut.TestCase(new_empty_section_contents(),
                        new_empty_section_contents(),
                        new_empty_section_contents(),
                        new_empty_section_contents(),
                        new_empty_section_contents())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
