import os
import pathlib

from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel, FileTypeAccess


class FileMatcherModelForDescribedPath(FileMatcherModel):
    def __init__(self, path: DescribedPath):
        self._path = path
        self._file_type_access = _FileTypeAccessForPath(path.primitive)

    @property
    def path(self) -> DescribedPath:
        """Path of the file to match. May or may not exist."""
        return self._path

    @property
    def file_type_access(self) -> FileTypeAccess:
        return self._file_type_access


class _FileTypeAccessForPath(FileTypeAccess):
    _IS_FILE_TYPE_FUNCTIONS = {
        FileType.REGULAR: pathlib.Path.is_file,
        FileType.DIRECTORY: pathlib.Path.is_dir,
        FileType.SYMLINK: pathlib.Path.is_symlink,
    }

    def __init__(self, path: pathlib.Path):
        self._path = path

    def is_type(self, expected: FileType) -> bool:
        return self._IS_FILE_TYPE_FUNCTIONS[expected](self._path)

    def stat(self, follow_sym_links=True) -> os.stat_result:
        return (
            self._path.stat()
            if follow_sym_links
            else
            self._path.lstat()
        )
