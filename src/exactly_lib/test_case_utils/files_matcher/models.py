import os
import pathlib
from abc import ABC, abstractmethod
from typing import Iterator, Optional, List

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.test_case_utils.file_matcher.file_matcher_models import FileMatcherModelForDescribedPath
from exactly_lib.test_case_utils.matcher.impls import combinator_matchers
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.type_system.logic.files_matcher import FileModel, FilesMatcherModel
from exactly_lib.type_system.logic.hard_error import HardErrorException


class FileModelForDir(FileModel):
    def __init__(self,
                 relative_to_root_dir: pathlib.Path,
                 path: DescribedPath,
                 ):
        self._relative_to_root_dir = relative_to_root_dir
        self._path = path

    @property
    def path(self) -> DescribedPath:
        return self._path

    @property
    def relative_to_root_dir(self) -> pathlib.Path:
        return self._relative_to_root_dir


class _FilesGenerator(ABC):
    @abstractmethod
    def generate(self, root_dir_path: DescribedPath) -> Iterator[FileModel]:
        pass


class _FilesMatcherModelForDir(FilesMatcherModel):
    def __init__(self,
                 dir_path: DescribedPath,
                 files_generator: _FilesGenerator,
                 files_selection: Optional[FileMatcher] = None,
                 ):
        self._dir_path = dir_path
        self._files_generator = files_generator
        self._files_selection = files_selection

    def sub_set(self, selector: FileMatcher) -> FilesMatcherModel:
        new_file_selector = (selector
                             if self._files_selection is None
                             else combinator_matchers.Conjunction([self._files_selection,
                                                                   selector])
                             )

        return _FilesMatcherModelForDir(self._dir_path,
                                        self._files_generator,
                                        new_file_selector,
                                        )

    def files(self) -> Iterator[FileModel]:
        file_models = self._files_generator.generate(self._dir_path)
        if self._files_selection is None:
            return file_models
        else:
            return (
                file_model
                for file_model in file_models
                if self._files_selection.matches_w_trace(FileMatcherModelForDescribedPath(file_model.path)).value
            )


def recursive(dir_path: DescribedPath,
              min_depth: Optional[int] = None,
              max_depth: Optional[int] = None) -> FilesMatcherModel:
    """
    Depth 0 is the direct contents of the model.
    """
    return _FilesMatcherModelForDir(dir_path,
                                    _FilesGeneratorForRecursive(min_depth, max_depth),
                                    None)


def non_recursive(dir_path: DescribedPath) -> FilesMatcherModel:
    return _FilesMatcherModelForDir(dir_path, _FilesGeneratorForNonRecursive(), None)


class _FilesGeneratorForNonRecursive(_FilesGenerator):
    def generate(self, root_dir_path: DescribedPath) -> Iterator[FileModel]:
        def mk_model(file_name: str) -> FileModel:
            return FileModelForDir(pathlib.Path(file_name),
                                   root_dir_path.child(file_name))

        return map(mk_model, os.listdir(str(root_dir_path.primitive)))


class _FilesGeneratorForRecursive(_FilesGenerator):
    def __init__(self,
                 min_depth: Optional[int] = None,
                 max_depth: Optional[int] = None,
                 ):
        self._min_depth = min_depth
        self._max_depth = max_depth

    def generate(self, root_dir_path: DescribedPath) -> Iterator[FileModel]:
        def add_dir_to_process_if_is_dir(maybe_entry_for_dir):
            try:
                if maybe_entry_for_dir.is_dir():
                    remaining_dirs.append(current_file.new_for_sub_dir(maybe_entry_for_dir))
            except OSError as ex:
                raise HardErrorException(
                    text_docs.os_exception_error_message(ex)
                )

        remaining_dirs = self._initialize_for_depth_0(root_dir_path)

        while remaining_dirs:
            current_file = remaining_dirs.pop(0)

            is_within_min_depth_limit = self._is_within_min_depth_limit(current_file.depth)
            is_not_at_max_depth = not self._is_at_max_depth_limit(current_file.depth)

            for dir_entry in current_file.dir_entries():
                if is_within_min_depth_limit:
                    yield current_file.file_model(dir_entry)
                if is_not_at_max_depth:
                    add_dir_to_process_if_is_dir(dir_entry)

    @staticmethod
    def _initialize_for_depth_0(root_dir_path: DescribedPath) -> List['_FilesInDir']:
        return [
            _FilesInDir(pathlib.Path(),
                        root_dir_path,
                        0)
        ]

    def _is_within_min_depth_limit(self, depth: int) -> bool:
        return self._min_depth is None or depth >= self._min_depth

    def _is_within_max_depth_limit(self, depth: int) -> bool:
        return self._max_depth is None or depth <= self._max_depth

    def _is_at_max_depth_limit(self, depth: int) -> bool:
        return self._max_depth is not None and depth == self._max_depth


class _FilesInDir:
    def __init__(self,
                 relative_parent: pathlib.Path,
                 absolute_parent: DescribedPath,
                 depth: int,
                 ):
        self._relative_parent = relative_parent
        self._absolute_parent = absolute_parent
        self.depth = depth

    def new_for_sub_dir(self, dir_entry) -> '_FilesInDir':
        return _FilesInDir(
            self._relative_parent / dir_entry.name,
            self._absolute_parent.child(dir_entry.name),
            self.depth + 1,
        )

    def file_model(self, dir_entry) -> FileModel:
        return FileModelForDir(
            self._relative_parent / dir_entry.name,
            self._absolute_parent.child(dir_entry.name),
        )

    def dir_entries(self) -> Iterator:  # Iterator[os.DirEntry]
        return os.scandir(str(self._absolute_parent.primitive))
