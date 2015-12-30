import pathlib
import stat

from shellcheck_lib_test.test_resources.file_utils import write_file


class FileSystemElement:
    def write_to(self,
                 parent_dir_path: pathlib.Path):
        raise NotImplementedError()


class File(FileSystemElement):
    def __init__(self,
                 file_name: str,
                 contents: str):
        self.file_name = file_name
        self.contents = contents

    def write_to(self,
                 parent_dir_path: pathlib.Path):
        write_file(parent_dir_path / self.file_name,
                   self.contents)


class _ExecutableFile(File):
    def __init__(self, file_name: str, contents: str):
        super().__init__(file_name, contents)

    def write_to(self,
                 parent_dir_path: pathlib.Path):
        file_path = parent_dir_path / self.file_name
        write_file(file_path,
                   self.contents)
        file_path.chmod(stat.S_IXOTH)


def executable_file(file_name: str,
                    contents: str = '') -> File:
    return _ExecutableFile(file_name, contents)


def empty_file(file_name: str) -> File:
    return File(file_name, '')


class Dir(FileSystemElement):
    def __init__(self,
                 file_name: str,
                 file_system_element_contents: list):
        self.file_name = file_name
        self.file_system_element_contents = file_system_element_contents

    def write_to(self,
                 parent_dir_path: pathlib.Path):
        dir_path = parent_dir_path / self.file_name
        dir_path.mkdir(parents=True)
        for file_element in self.file_system_element_contents:
            file_element.write_to(dir_path)


def empty_dir(file_name: str) -> Dir:
    return Dir(file_name, [])


class Link(FileSystemElement):
    def __init__(self,
                 file_name: str,
                 target: str):
        self.file_name = file_name
        self.target = target

    def write_to(self,
                 parent_dir_path: pathlib.Path):
        target_path = parent_dir_path / self.target
        file_path = parent_dir_path / self.file_name
        target_is_dir = target_path.is_dir()
        file_path.symlink_to(target_path, target_is_dir)


def sym_link(file_name: str,
             target: str) -> Link:
    return Link(file_name, target)


class DirContents:
    def __init__(self,
                 file_system_element_contents: list):
        self.file_system_element_contents = file_system_element_contents

    def write_to(self,
                 dir_path: pathlib.Path):
        for file_element in self.file_system_element_contents:
            assert isinstance(file_element, FileSystemElement)
            file_element.write_to(dir_path)


def empty_dir_contents() -> DirContents:
    return DirContents([])
