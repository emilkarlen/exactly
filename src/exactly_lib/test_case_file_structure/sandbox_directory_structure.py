import pathlib
import tempfile
from pathlib import Path

from exactly_lib import program_info

TMP_INTERNAL__STDIN_CONTENTS = 'stdin.txt'

TMP_INTERNAL__WITH_REPLACED_ENV_VARS_SUB_DIR = 'with-replaced-env-vars'

LOG__PHASE_SUB_DIR = 'phase'

SUB_DIR_FOR_REPLACEMENT_SOURCES_UNDER_ACT_DIR = 'act'

SUB_DIR_FOR_REPLACEMENT_SOURCES_NOT_UNDER_ACT_DIR = 'global'

SUB_DIRECTORY__ACT = 'act'

SUB_DIRECTORY__TMP = 'tmp'
SUB_DIRECTORY__TMP_USER = 'user'
SUB_DIRECTORY__TMP_INTERNAL = 'internal'

PATH__TMP_USER = SUB_DIRECTORY__TMP + '/' + SUB_DIRECTORY__TMP_USER

SUB_DIRECTORY__RESULT = 'result'

RESULT_FILE__STDERR = 'stderr'
RESULT_FILE__STDOUT = 'stdout'
RESULT_FILE__EXITCODE = 'exitcode'

RESULT_FILE_ALL = (
    RESULT_FILE__STDERR,
    RESULT_FILE__STDOUT,
    RESULT_FILE__EXITCODE,
)


class DirWithSubDirs:
    """Name of a directory together with a list of sub directories"""

    def __init__(self, name: str,
                 sub_dirs: list):
        self.name = name
        self.sub_dirs = sub_dirs

    def mk_dirs(self, existing_root_dir: Path):
        this_dir = existing_root_dir / self.name
        this_dir.mkdir()
        for sub_dir in self.sub_dirs:
            sub_dir.mk_dirs(this_dir)


def empty_dir(name: str) -> DirWithSubDirs:
    return DirWithSubDirs(name, [])


execution_directories = [
    empty_dir('testcase'),
    empty_dir(SUB_DIRECTORY__ACT),
    DirWithSubDirs(SUB_DIRECTORY__TMP, [
        empty_dir(SUB_DIRECTORY__TMP_INTERNAL),
        empty_dir(SUB_DIRECTORY__TMP_USER)
    ]),
    empty_dir(SUB_DIRECTORY__RESULT),
    empty_dir('log'),
]


class DirWithRoot:
    def __init__(self,
                 root_dir: Path):
        self.__root_dir = root_dir

    @property
    def root_dir(self) -> Path:
        return self.__root_dir


class Result(DirWithRoot):
    def __init__(self, root_dir: Path):
        super().__init__(root_dir)
        self.__exitcode_file = self.root_dir / RESULT_FILE__EXITCODE
        self.__stdout_file = self.root_dir / RESULT_FILE__STDOUT
        self.__stderr_file = self.root_dir / RESULT_FILE__STDERR

    @property
    def exitcode_file(self) -> Path:
        return self.__exitcode_file

    @property
    def stdout_file(self) -> Path:
        return self.__stdout_file

    @property
    def stderr_file(self) -> Path:
        return self.__stderr_file


class Tmp(DirWithRoot):
    def __init__(self, root_dir: Path):
        super().__init__(root_dir)
        self.__internal_dir = self.root_dir / SUB_DIRECTORY__TMP_INTERNAL
        self.__user_dir = self.root_dir / SUB_DIRECTORY__TMP_USER

    @property
    def internal_dir(self) -> Path:
        return self.__internal_dir

    @property
    def user_dir(self) -> Path:
        return self.__user_dir


class SandboxDirectoryStructure(DirWithRoot):
    """
    The temporary directory structure in which (parts of) a test case is executed
    """

    def __init__(self, dir_name: str):
        super().__init__(Path(dir_name))
        self.__test_case_dir = self.root_dir / 'testcase'
        self.__act_dir = self.root_dir / SUB_DIRECTORY__ACT
        self.__tmp = Tmp(self.root_dir / SUB_DIRECTORY__TMP)
        self.__result = Result(self.root_dir / SUB_DIRECTORY__RESULT)
        self.__log_dir = self.root_dir / 'log'

    @property
    def test_case_dir(self) -> Path:
        return self.__test_case_dir

    @property
    def act_dir(self) -> Path:
        return self.__act_dir

    @property
    def result(self) -> Result:
        return self.__result

    @property
    def tmp(self) -> Tmp:
        return self.__tmp

    @property
    def log_dir(self) -> Path:
        return self.__log_dir

    def relative_to_sds_root(self, file_in_sub_dir: pathlib.PurePath) -> pathlib.PurePath:
        return file_in_sub_dir.relative_to(self.root_dir)


def construct_at(execution_directory_root: str) -> SandboxDirectoryStructure:
    for d in execution_directories:
        d.mk_dirs(Path(execution_directory_root))
    return SandboxDirectoryStructure(execution_directory_root)


def construct_at_tmp_root() -> SandboxDirectoryStructure:
    root_dir_name = tempfile.mkdtemp(prefix=program_info.PROGRAM_NAME + '-')
    return construct_at(root_dir_name)


def root_dir_for_non_stdout_or_stderr_files_with_replaced_env_vars(sds: SandboxDirectoryStructure) -> Path:
    return sds.tmp.internal_dir / TMP_INTERNAL__WITH_REPLACED_ENV_VARS_SUB_DIR


def stdin_contents_file(sds: SandboxDirectoryStructure) -> Path:
    return sds.tmp.internal_dir / TMP_INTERNAL__STDIN_CONTENTS


def sds_log_phase_dir(sds: SandboxDirectoryStructure,
                      phase_name: str) -> Path:
    return log_phase_dir(sds.log_dir, phase_name)


def log_phase_dir(log_root_dir: Path,
                  phase_name: str) -> Path:
    return log_root_dir / LOG__PHASE_SUB_DIR / phase_name
