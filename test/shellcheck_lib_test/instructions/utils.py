from contextlib import contextmanager
import os
import pathlib
import tempfile

from shellcheck_lib.test_case import instructions as i
from shellcheck_lib.execution import execution_directory_structure
from shellcheck_lib_test.util.file_utils import write_file


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
