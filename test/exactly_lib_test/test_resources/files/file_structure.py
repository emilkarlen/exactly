import pathlib
from abc import abstractmethod, ABC
from typing import Sequence, List

from exactly_lib.impls.file_properties import FileType
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.test_resources.files import executable_files
from exactly_lib_test.test_resources.files.file_utils import write_file
from exactly_lib_test.test_resources.programs import python_program_execution


class FileSystemElement(ABC):
    def write_to(self,
                 parent_dir_path: pathlib.Path):
        raise NotImplementedError()

    @property
    def name(self) -> str:
        return ''

    @property
    @abstractmethod
    def file_type(self) -> FileType:
        raise NotImplementedError('abstract method')

    @property
    def name_as_path(self) -> pathlib.Path:
        return pathlib.Path(self.name)


FileSystemElements = Sequence[FileSystemElement]


class File(FileSystemElement):
    def __init__(self,
                 file_name: str,
                 contents: str):
        self.file_name = file_name
        self.contents = contents

    @staticmethod
    def empty(file_name: str) -> 'File':
        return File(file_name, '')

    @property
    def name(self) -> str:
        return self.file_name

    @property
    def file_type(self) -> FileType:
        return FileType.REGULAR

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
        executable_files.make_executable_by_os(file_path)


class _ExecutableFileWithPythonSourceCode(File):
    def __init__(self, file_name: str, python_source_code: str):
        super().__init__(file_name, python_source_code)

    def write_to(self,
                 parent_dir_path: pathlib.Path):
        file_path = parent_dir_path / self.file_name
        python_program_execution.write_executable_file_with_python_source(
            file_path,
            self.contents)


def executable_file(file_name: str,
                    contents: str = '') -> File:
    return _ExecutableFile(file_name, contents)


def python_executable_file(executable_file_name_for_invokation_at_command_line: str,
                           python_source_code: str = '') -> File:
    return _ExecutableFileWithPythonSourceCode(executable_file_name_for_invokation_at_command_line, python_source_code)


def file_with_lines(name: str, contents: Sequence[str]) -> File:
    return File(name, lines_content(contents))


class Dir(FileSystemElement):
    def __init__(self,
                 file_name: str,
                 file_system_element_contents: Sequence[FileSystemElement]):
        self.file_name = file_name
        self.file_system_element_contents = file_system_element_contents

    @staticmethod
    def empty(file_name: str) -> 'Dir':
        return Dir(file_name, [])

    @property
    def name(self) -> str:
        return self.file_name

    @property
    def file_type(self) -> FileType:
        return FileType.DIRECTORY

    def write_to(self,
                 parent_dir_path: pathlib.Path):
        dir_path = parent_dir_path / self.file_name
        dir_path.mkdir(parents=True)
        for file_element in self.file_system_element_contents:
            file_element.write_to(dir_path)


class Link(FileSystemElement):
    def __init__(self,
                 file_name: str,
                 target: str):
        self.file_name = file_name
        self.target = target

    @property
    def name(self) -> str:
        return self.file_name

    @property
    def file_type(self) -> FileType:
        return FileType.SYMLINK

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
                 file_system_element_contents: FileSystemElements):
        self._file_system_element_contents = file_system_element_contents

    @staticmethod
    def empty() -> 'DirContents':
        return DirContents([])

    def write_to(self, dir_path: pathlib.Path):
        for file_element in self._file_system_element_contents:
            assert isinstance(file_element, FileSystemElement)
            file_element.write_to(dir_path)

    @property
    def file_system_elements(self) -> List[FileSystemElement]:
        return list(self._file_system_element_contents)

    def in_dir(self, parent_dir: str):
        return DirContents([
            Dir(parent_dir, self.file_system_elements)
        ])

    def in_dir_path(self, parent_dir: pathlib.Path):
        return DirContents([
            Dir(str(parent_dir), self.file_system_elements)
        ])


def add_dir_contents(dir_contents_sequence: Sequence[DirContents]) -> DirContents:
    elements = []
    for dc in dir_contents_sequence:
        elements += dc.file_system_elements
    return DirContents(elements)


def empty_dir_contents() -> DirContents:
    return DirContents([])
