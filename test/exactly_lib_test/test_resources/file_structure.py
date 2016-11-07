import pathlib

import exactly_lib_test.test_resources.programs.python_program_execution
from exactly_lib_test.test_resources.file_utils import write_file
from exactly_lib_test.test_resources.files import executable_files


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
        executable_files.make_executable_by_os(file_path)


class _ExecutableFileWithPythonSourceCode(File):
    def __init__(self, file_name: str, python_source_code: str):
        super().__init__(file_name, python_source_code)

    def write_to(self,
                 parent_dir_path: pathlib.Path):
        file_path = parent_dir_path / self.file_name
        exactly_lib_test.test_resources.programs.python_program_execution.write_executable_file_with_python_source(
            file_path,
            self.contents)


def executable_file(file_name: str,
                    contents: str = '') -> File:
    return _ExecutableFile(file_name, contents)


def python_executable_file(executable_file_name_for_invokation_at_command_line: str,
                           python_source_code: str = '') -> File:
    return _ExecutableFileWithPythonSourceCode(executable_file_name_for_invokation_at_command_line, python_source_code)


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
