import os
import tempfile
from contextlib import contextmanager
from time import strftime, localtime

from exactly_lib import program_info
from exactly_lib.test_case import sandbox_directory_structure as sds_module
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.file_utils import resolved_path_name, resolved_path, preserved_cwd
from exactly_lib_test.test_resources.execution import sds_populator, home_or_sds_populator
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


class SdsAction:
    def apply(self, sds: SandboxDirectoryStructure):
        pass


class HomeAndSdsAction:
    def apply(self, home_and_sds: HomeAndSds):
        pass


class MkDirIfNotExistsAndChangeToIt(SdsAction):
    def __init__(self, sds_2_dir_path):
        self.sds_2_dir_path = sds_2_dir_path

    def apply(self, sds: SandboxDirectoryStructure):
        dir_path = self.sds_2_dir_path(sds)
        dir_path.mkdir(parents=True, exist_ok=True)
        os.chdir(str(dir_path))


def mk_sub_dir_of_act_and_change_to_it(sub_dir_name: str) -> SdsAction:
    return MkDirIfNotExistsAndChangeToIt(lambda sds: sds.act_dir / sub_dir_name)


class HomeAndSdsContents(tuple):
    def __new__(cls,
                home_dir_contents: DirContents = empty_dir_contents(),
                sds_contents: sds_populator.SdsPopulator = sds_populator.empty()):
        return tuple.__new__(cls, (home_dir_contents,
                                   sds_contents))

    @property
    def home_dir_contents(self) -> DirContents:
        return self[0]

    @property
    def sds_contents(self) -> sds_populator.SdsPopulator:
        return self[1]


@contextmanager
def home_and_sds_with_act_as_curr_dir(
        home_dir_contents: DirContents = empty_dir_contents(),
        sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
        home_or_sds_contents: home_or_sds_populator.HomeOrSdsPopulator = home_or_sds_populator.empty(),
        pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction()) -> HomeAndSds:
    prefix = strftime(program_info.PROGRAM_NAME + '-test-%Y-%m-%d-%H-%M-%S', localtime())
    with tempfile.TemporaryDirectory(prefix=prefix + "-home-") as home_dir:
        home_dir_path = resolved_path(home_dir)
        with sandbox_directory_structure(prefix=prefix + "-sds-",
                                         contents=sds_contents) as sds:
            ret_val = HomeAndSds(home_dir_path, sds)
            with preserved_cwd():
                os.chdir(str(sds.act_dir))
                pre_contents_population_action.apply(ret_val)
                home_dir_contents.write_to(home_dir_path)
                home_or_sds_contents.write_to(ret_val)
                yield ret_val


@contextmanager
def sds_with_act_as_curr_dir(contents: sds_populator.SdsPopulator = sds_populator.empty(),
                             pre_contents_population_action: SdsAction = SdsAction(),
                             ) -> sds_module.SandboxDirectoryStructure:
    with tempfile.TemporaryDirectory(prefix=program_info.PROGRAM_NAME + '-test-sds-') as sds_root_dir:
        sds = sds_module.construct_at(resolved_path_name(sds_root_dir))
        with preserved_cwd():
            os.chdir(str(sds.act_dir))
            pre_contents_population_action.apply(sds)
            contents.apply(sds)
            yield sds


@contextmanager
def sandbox_directory_structure(contents: sds_populator.SdsPopulator = sds_populator.empty(),
                                prefix: str = program_info.PROGRAM_NAME + '-test-sds-') \
        -> sds_module.SandboxDirectoryStructure:
    with tempfile.TemporaryDirectory(prefix=prefix) as sds_root_dir:
        sds = sds_module.construct_at(resolved_path_name(sds_root_dir))
        contents.apply(sds)
        yield sds
