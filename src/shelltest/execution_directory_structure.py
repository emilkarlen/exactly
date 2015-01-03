__author__ = 'emil'


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
    DirWithSubDirs('result',
                   [DirWithSubDirs('std', [])]),
    DirWithSubDirs('test', []),
    DirWithSubDirs('testcase', []),
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
    def exitcode_file(self) -> Std:
        return self.__exitcode_file


class TestCase(DirWithRoot):
    def __init__(self, parent_dir: Path):
        super().__init__(parent_dir / 'testcase')
        self.__apply_file = self.root_dir / 'apply.sh'
        self.__main_file = self.root_dir / 'main.sh'

    @property
    def apply_file(self) -> Path:
        return self.__apply_file

    @property
    def main_file(self) -> Path:
        return self.__main_file


class TestRootDir(DirWithRoot):
    def __init__(self, dir_name: str):
        super().__init__(Path(dir_name))
        self.__test_dir = self.root_dir / 'test'
        self.__result = Result(self.root_dir)
        self.__test_case = TestCase(self.root_dir)

    @property
    def test_dir(self) -> Path:
        return self.__test_dir

    @property
    def result(self) -> Result:
        return self.__result

    @property
    def test_case(self) -> TestCase:
        return self.__test_case


def construct_at(execution_directory_root: str) -> TestRootDir:
    for d in execution_directories:
        d.mk_dirs(Path(Path(execution_directory_root)))
    return TestRootDir(execution_directory_root)


def construct_at_tmp_root() -> TestRootDir:
    root_dir_name = tempfile.TemporaryDirectory(prefix='shelltest-')
    return construct_at(root_dir_name)
