import os
import pathlib
from abc import ABC, abstractmethod
from typing import Iterator, Optional

from exactly_lib.test_case_utils.file_matcher.file_matcher_models import FileMatcherModelForDescribedPath
from exactly_lib.test_case_utils.matcher.impls import combinator_matchers
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.type_system.logic.files_matcher import FileModel, FilesMatcherModel


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


def recursive(dir_path: DescribedPath) -> FilesMatcherModel:
    return _FilesMatcherModelForDir(dir_path, _FilesGeneratorForRecursive(), None)


def non_recursive(dir_path: DescribedPath) -> FilesMatcherModel:
    return _FilesMatcherModelForDir(dir_path, _FilesGeneratorForNonRecursive(), None)


class _FilesGeneratorForNonRecursive(_FilesGenerator):
    def generate(self, root_dir_path: DescribedPath) -> Iterator[FileModel]:
        def mk_model(file_name: str) -> FileModel:
            return FileModelForDir(pathlib.Path(file_name),
                                   root_dir_path.child(file_name))

        return map(mk_model, os.listdir(str(root_dir_path.primitive)))


class _FilesGeneratorForRecursive(_FilesGenerator):
    def generate(self, root_dir_path: DescribedPath) -> Iterator[FileModel]:
        remaining_dirs = [
            _FilesInDir(pathlib.Path(),
                        root_dir_path)
        ]

        while remaining_dirs:
            fid = remaining_dirs.pop(0)
            for dir_entry in fid.dir_entries():
                yield fid.file_model(dir_entry)
                if dir_entry.is_dir():
                    remaining_dirs.append(fid.new_for_sub_dir(dir_entry))


class _FilesInDir:
    def __init__(self,
                 relative_parent: pathlib.Path,
                 absolute_parent: DescribedPath,
                 ):
        self._relative_parent = relative_parent
        self._absolute_parent = absolute_parent

    def new_for_sub_dir(self, dir_entry) -> '_FilesInDir':
        return _FilesInDir(
            self._relative_parent / dir_entry.name,
            self._absolute_parent.child(dir_entry.name)
        )

    def file_model(self, dir_entry) -> FileModel:
        return FileModelForDir(
            self._relative_parent / dir_entry.name,
            self._absolute_parent.child(dir_entry.name),
        )

    def dir_entries(self) -> Iterator:  # Iterator[os.DirEntry]
        return os.scandir(str(self._absolute_parent.primitive))
