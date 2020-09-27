import pathlib
import tempfile
from pathlib import Path
from typing import List

from exactly_lib import program_info
from exactly_lib.tcfs.path_relativity import RelSdsOptionType
from exactly_lib.util.process_execution import process_output_files

LOG__PHASE_SUB_DIR = 'phase'

SUB_DIRECTORY__ACT = 'act'
SUB_DIRECTORY__TMP_USER = 'tmp'
SUB_DIRECTORY__RESULT = 'result'

SUB_DIRECTORY__INTERNAL = 'internal'

SUB_DIRECTORY__TMP_INTERNAL = 'tmp'
SUB_DIRECTORY__LOG = 'log'

INSTRUCTION_SUB_DIR_FOR_VALIDATION = 'validate'

PATH__TMP_USER = SUB_DIRECTORY__TMP_USER

RESULT_FILE__STDERR = process_output_files.STDERR_FILE_NAME
RESULT_FILE__STDOUT = process_output_files.STDOUT_FILE_NAME
RESULT_FILE__EXITCODE = process_output_files.EXIT_CODE_FILE_NAME

RESULT_FILE_ALL = (
    RESULT_FILE__STDERR,
    RESULT_FILE__STDOUT,
    RESULT_FILE__EXITCODE,
)

TMP_INTERNAL__STDIN_CONTENTS = 'stdin.txt'


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


SDS_SUB_DIRECTORIES = {
    RelSdsOptionType.REL_ACT: pathlib.PurePosixPath(SUB_DIRECTORY__ACT),
    RelSdsOptionType.REL_TMP: pathlib.PurePosixPath(SUB_DIRECTORY__TMP_USER),
    RelSdsOptionType.REL_RESULT: pathlib.PurePosixPath(SUB_DIRECTORY__RESULT),
}

DIRECTORIES = (
        [
            empty_dir(str(path))
            for path in SDS_SUB_DIRECTORIES.values()
        ] +
        [
            DirWithSubDirs(SUB_DIRECTORY__INTERNAL, [
                empty_dir(SUB_DIRECTORY__TMP_INTERNAL),
                empty_dir(SUB_DIRECTORY__LOG),
            ]),
        ]
)


class DirWithRoot:
    def __init__(self, root_dir: Path):
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

    @property
    def all_files(self) -> List[Path]:
        return [
            self.exitcode_file,
            self.stdout_file,
            self.stderr_file,
        ]


class Internal(DirWithRoot):
    def __init__(self, root_dir: Path):
        super().__init__(root_dir)
        self.__tmp_dir = self.root_dir / SUB_DIRECTORY__TMP_INTERNAL
        self.__log_dir = self.root_dir / SUB_DIRECTORY__LOG

    @property
    def tmp_dir(self) -> Path:
        return self.__tmp_dir

    @property
    def log_dir(self) -> Path:
        return self.__log_dir


class SandboxDs(DirWithRoot):
    """
    The temporary directory structure in which (parts of) a test case is executed
    """

    def __init__(self, dir_name: str):
        super().__init__(Path(dir_name))
        self.__act_dir = self.root_dir / SDS_SUB_DIRECTORIES[RelSdsOptionType.REL_ACT]
        self.__user_tmp = self.root_dir / SDS_SUB_DIRECTORIES[RelSdsOptionType.REL_TMP]
        self.__result = Result(self.root_dir / SDS_SUB_DIRECTORIES[RelSdsOptionType.REL_RESULT])
        self.__internal = Internal(self.root_dir / SUB_DIRECTORY__INTERNAL)

    @property
    def act_dir(self) -> Path:
        return self.__act_dir

    @property
    def user_tmp_dir(self) -> Path:
        return self.__user_tmp

    @property
    def result(self) -> Result:
        return self.__result

    @property
    def result_dir(self) -> Path:
        return self.__result.root_dir

    @property
    def internal_tmp_dir(self) -> Path:
        return self.__internal.tmp_dir

    @property
    def log_dir(self) -> Path:
        return self.__internal.log_dir

    def relative_to_sds_root(self, file_in_sub_dir: pathlib.PurePath) -> pathlib.PurePath:
        return file_in_sub_dir.relative_to(self.root_dir)

    def all_leaf_dirs__except_result(self) -> List[Path]:
        return [
            self.act_dir,
            self.user_tmp_dir,
            self.internal_tmp_dir,
            self.log_dir,
        ]

    def all_leaf_dirs__including_result(self) -> List[Path]:
        return self.all_leaf_dirs__except_result() + [self.result.root_dir]

    def all_root_dirs__including_result(self) -> List[Path]:
        return [
            self.act_dir,
            self.user_tmp_dir,
            self.result.root_dir,
            self.__internal.root_dir,
        ]


def construct_at(directory_root: str) -> SandboxDs:
    for d in DIRECTORIES:
        d.mk_dirs(Path(directory_root))
    return SandboxDs(directory_root)


def construct_at_tmp_root() -> SandboxDs:
    root_dir_name = tempfile.mkdtemp(prefix=program_info.PROGRAM_NAME + '-')
    return construct_at(root_dir_name)


def stdin_contents_file(sds: SandboxDs) -> Path:
    return sds.internal_tmp_dir / TMP_INTERNAL__STDIN_CONTENTS
