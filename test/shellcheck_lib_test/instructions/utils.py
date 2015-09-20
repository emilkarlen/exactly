from contextlib import contextmanager
import os
import pathlib
import tempfile
from time import strftime, localtime

from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.test_case.instruction import common as i
from shellcheck_lib.execution import execution_directory_structure
from shellcheck_lib_test.util.file_utils import write_file


class ActResult:
    def __init__(self,
                 exitcode: int=0,
                 stdout_contents: str='',
                 stderr_contents: str=''):
        self._exitcode = exitcode
        self._stdout_contents = stdout_contents
        self._stderr_contents = stderr_contents

    @property
    def exitcode(self) -> int:
        return self._exitcode

    @property
    def stdout_contents(self) -> str:
        return self._stdout_contents

    @property
    def stderr_contents(self) -> str:
        return self._stderr_contents


@contextmanager
def act_phase_result(exitcode: int=0,
                     stdout_contents: str='',
                     stderr_contents: str='') -> i.GlobalEnvironmentForPostEdsPhase:
    cwd_before = os.getcwd()
    home_dir_path = pathlib.Path(cwd_before)
    with tempfile.TemporaryDirectory(prefix='shellcheck-test-') as eds_root_dir:
        eds = execution_directory_structure.construct_at(eds_root_dir)
        write_file(eds.result.exitcode_file, str(exitcode))
        write_file(eds.result.std.stdout_file, stdout_contents)
        write_file(eds.result.std.stderr_file, stderr_contents)
        try:
            os.chdir(str(eds.test_root_dir))
            yield i.GlobalEnvironmentForPostEdsPhase(home_dir_path,
                                                     eds)
        finally:
            os.chdir(cwd_before)


class HomeAndEds:
    def __init__(self,
                 home_path: pathlib.Path,
                 eds: ExecutionDirectoryStructure):
        self._home_path = home_path
        self._eds = eds

    @property
    def home_dir_path(self) -> pathlib.Path:
        return self._home_path

    @property
    def eds(self) -> ExecutionDirectoryStructure:
        return self._eds

    def write_act_result(self,
                         result: ActResult):
        write_file(self.eds.result.exitcode_file, str(result.exitcode))
        write_file(self.eds.result.std.stdout_file, result.stdout_contents)
        write_file(self.eds.result.std.stderr_file, result.stderr_contents)


@contextmanager
def home_and_eds_and_test_as_curr_dir() -> HomeAndEds:
    cwd_before = os.getcwd()
    prefix = strftime("shellcheck-test-%Y-%m-%d-%H-%M-%S", localtime())
    with tempfile.TemporaryDirectory(prefix=prefix + "-home-") as home_dir:
        home_dir_path = pathlib.Path(home_dir)
        with tempfile.TemporaryDirectory(prefix=prefix + "-eds-") as eds_root_dir:
            eds = execution_directory_structure.construct_at(eds_root_dir)
            try:
                os.chdir(str(eds.test_root_dir))
                yield HomeAndEds(home_dir_path,
                                 eds)
            finally:
                os.chdir(cwd_before)
