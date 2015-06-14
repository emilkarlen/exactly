import tempfile
from pathlib import Path


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


execution_directories = [
    DirWithSubDirs('testcase', []),
    DirWithSubDirs('tmp', []),
    DirWithSubDirs('test', []),
    DirWithSubDirs('result',
                   [DirWithSubDirs('std', [])]),
    DirWithSubDirs('log', []),
]


class DirWithRoot:
    def __init__(self,
                 root_dir: Path):
        self.__root_dir = root_dir

    @property
    def root_dir(self) -> Path:
        return self.__root_dir


class Std(DirWithRoot):
    def __init__(self, parent_dir: Path):
        super().__init__(parent_dir / 'std')
        self.__stdout_file = self.root_dir / 'stdout'
        self.__stderr_file = self.root_dir / 'stderr'

    @property
    def stdout_file(self) -> Path:
        return self.__stdout_file

    @property
    def stderr_file(self) -> Path:
        return self.__stderr_file


class Result(DirWithRoot):
    def __init__(self, parent_dir: Path):
        super().__init__(parent_dir / 'result')
        self.__std = Std(self.root_dir)
        self.__exitcode_file = self.root_dir / 'exitcode'

    @property
    def std(self) -> Std:
        return self.__std

    @property
    def exitcode_file(self) -> Path:
        return self.__exitcode_file


class ExecutionDirectoryStructure(DirWithRoot):
    def __init__(self, dir_name: str):
        super().__init__(Path(dir_name))
        self.__test_case_dir = self.root_dir / 'testcase'
        self.__test_dir = self.root_dir / 'test'
        self.__tmp_dir = self.root_dir / 'tmp'
        self.__result = Result(self.root_dir)
        self.__log_dir = self.root_dir / 'log'

    @property
    def test_case_dir(self) -> Path:
        return self.__test_case_dir

    @property
    def test_root_dir(self) -> Path:
        return self.__test_dir

    @property
    def tmp_dir(self) -> Path:
        return self.__tmp_dir

    @property
    def result(self) -> Result:
        return self.__result

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
