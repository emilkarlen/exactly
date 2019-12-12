from typing import Callable

from exactly_lib.type_system.logic.files_matcher import FilesMatcher, FilesMatcherConstructor
from exactly_lib.util.file_utils import TmpDirFileSpace


class ConstantConstructor(FilesMatcherConstructor):
    def __init__(self, constant: FilesMatcher):
        self._constant = constant

    def construct(self, tmp_files_space: TmpDirFileSpace) -> FilesMatcher:
        return self._constant


class ConstructorFromFunction(FilesMatcherConstructor):
    def __init__(self, constructor: Callable[[TmpDirFileSpace], FilesMatcher]):
        self._constructor = constructor

    def construct(self, tmp_files_space: TmpDirFileSpace) -> FilesMatcher:
        return self._constructor(tmp_files_space)
