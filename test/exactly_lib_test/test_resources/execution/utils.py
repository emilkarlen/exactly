import os

from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_resources.execution.sds_check.sds_utils import SdsAction
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


class MkDirIfNotExistsAndChangeToIt(SdsAction):
    def __init__(self, sds_2_dir_path):
        self.sds_2_dir_path = sds_2_dir_path

    def apply(self, sds: SandboxDirectoryStructure):
        dir_path = self.sds_2_dir_path(sds)
        dir_path.mkdir(parents=True, exist_ok=True)
        os.chdir(str(dir_path))


def mk_sub_dir_of_act_and_change_to_it(sub_dir_name: str) -> SdsAction:
    return MkDirIfNotExistsAndChangeToIt(lambda sds: sds.act_dir / sub_dir_name)


