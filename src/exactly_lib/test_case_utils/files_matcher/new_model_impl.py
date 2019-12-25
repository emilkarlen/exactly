import os
import pathlib
from typing import Iterator, Optional

from exactly_lib.test_case_utils.file_matcher import file_matchers
from exactly_lib.test_case_utils.matcher.impls import combinator_matchers
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.type_system.logic.files_matcher import FileModel, FilesMatcherModel


class FileModelForDir(FileModel):
    def __init__(self,
                 file_name: str,
                 root_dir: DescribedPath):
        self._relative_to_root_dir = pathlib.Path(file_name)
        self._path = root_dir.child(file_name)

    @property
    def path(self) -> DescribedPath:
        return self._path

    @property
    def relative_to_root_dir(self) -> pathlib.Path:
        return self._relative_to_root_dir


class FilesMatcherModelForDir(FilesMatcherModel):
    def __init__(self,
                 dir_path: DescribedPath,
                 files_selection: Optional[FileMatcher] = None,
                 ):
        self._dir_path = dir_path
        self._files_selection = files_selection

    def sub_set(self, selector: FileMatcher) -> FilesMatcherModel:
        new_file_selector = (selector
                             if self._files_selection is None
                             else combinator_matchers.Conjunction([self._files_selection,
                                                                   selector])
                             )

        return FilesMatcherModelForDir(self._dir_path,
                                       new_file_selector,
                                       )

    def files(self) -> Iterator[FileModel]:
        def mk_model(file_name: str) -> FileModel:
            return FileModelForDir(file_name, self._dir_path)

        if self._files_selection is None:
            return map(mk_model, os.listdir(str(self._dir_path.primitive)))
        else:
            file_names = file_matchers.matching_files_in_dir(self._files_selection,
                                                             self._dir_path)
            return map(mk_model, file_names)
