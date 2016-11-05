import os
import tempfile
from contextlib import contextmanager
from time import strftime, localtime

from exactly_lib import program_info
from exactly_lib.test_case import sandbox_directory_structure as eds_module
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.file_utils import resolved_path_name, resolved_path
from exactly_lib_test.test_resources.execution import sds_populator
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir_contents
from exactly_lib_test.test_resources.file_utils import write_file


class ActResult:
    def __init__(self,
                 exitcode: int = 0,
                 stdout_contents: str = '',
                 stderr_contents: str = ''):
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


def write_act_result(sds: SandboxDirectoryStructure,
                     result: ActResult):
    write_file(sds.result.exitcode_file, str(result.exitcode))
    write_file(sds.result.stdout_file, result.stdout_contents)
    write_file(sds.result.stderr_file, result.stderr_contents)


class HomeAndSdsContents(tuple):
    def __new__(cls,
                home_dir_contents: DirContents = empty_dir_contents(),
                eds_contents: sds_populator.EdsPopulator = sds_populator.empty()):
        return tuple.__new__(cls, (home_dir_contents,
                                   eds_contents))

    @property
    def home_dir_contents(self) -> DirContents:
        return self[0]

    @property
    def sds_contents(self) -> sds_populator.EdsPopulator:
        return self[1]


@contextmanager
def home_and_sds_and_test_as_curr_dir(
        home_dir_contents: DirContents = empty_dir_contents(),
        eds_contents: sds_populator.EdsPopulator = sds_populator.empty()) -> HomeAndSds:
    cwd_before = os.getcwd()
    prefix = strftime(program_info.PROGRAM_NAME + '-test-%Y-%m-%d-%H-%M-%S', localtime())
    with tempfile.TemporaryDirectory(prefix=prefix + "-home-") as home_dir:
        home_dir_path = resolved_path(home_dir)
        home_dir_contents.write_to(home_dir_path)
        with sandbox_directory_structure(prefix=prefix + "-sds-",
                                         contents=eds_contents) as sds:
            try:
                os.chdir(str(sds.act_dir))
                yield HomeAndSds(home_dir_path,
                                 sds)
            finally:
                os.chdir(cwd_before)


@contextmanager
def sandbox_directory_structure(contents: sds_populator.EdsPopulator = sds_populator.empty(),
                                prefix: str = program_info.PROGRAM_NAME + '-test-sds-') \
        -> eds_module.SandboxDirectoryStructure:
    with tempfile.TemporaryDirectory(prefix=prefix) as eds_root_dir:
        sds = eds_module.construct_at(resolved_path_name(eds_root_dir))
        contents.apply(sds)
        yield sds
