import tempfile
from pathlib import Path

TMP_INTERNAL__WITH_REPLACED_ENV_VARS_SUB_DIR = 'with-replaced-env-vars'

SUB_DIR_FOR_REPLACEMENT_SOURCES_UNDER_ACT_DIR = 'act'

SUB_DIR_FOR_REPLACEMENT_SOURCES_NOT_UNDER_ACT_DIR = 'global'

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
    empty_dir('act'),
    DirWithSubDirs('tmp', [
        empty_dir('internal'),
        empty_dir('user')
    ]),
    empty_dir('result'),
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
        self.__exitcode_file = self.root_dir / 'exitcode'
        self.__stdout_file = self.root_dir / 'stdout'
        self.__stderr_file = self.root_dir / 'stderr'

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
        self.__internal_dir = self.root_dir / 'internal'
        self.__user_dir = self.root_dir / 'user'

    @property
    def internal_dir(self) -> Path:
        return self.__internal_dir

    @property
    def user_dir(self) -> Path:
        return self.__user_dir


class ExecutionDirectoryStructure(DirWithRoot):
    def __init__(self, dir_name: str):
        super().__init__(Path(dir_name))
        self.__test_case_dir = self.root_dir / 'testcase'
        self.__act_dir = self.root_dir / 'act'
        self.__tmp = Tmp(self.root_dir / 'tmp')
        self.__result = Result(self.root_dir / 'result')
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


def construct_at(execution_directory_root: str) -> ExecutionDirectoryStructure:
    for d in execution_directories:
        d.mk_dirs(Path(execution_directory_root))
    return ExecutionDirectoryStructure(execution_directory_root)


def construct_at_tmp_root() -> ExecutionDirectoryStructure:
    root_dir_name = tempfile.mkdtemp(prefix='shellcheck-')
    return construct_at(root_dir_name)


def root_dir_for_non_stdout_or_stderr_files_with_replaced_env_vars(eds: ExecutionDirectoryStructure) -> Path:
    return eds.tmp.internal_dir / TMP_INTERNAL__WITH_REPLACED_ENV_VARS_SUB_DIR
