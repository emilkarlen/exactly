import pathlib
from abc import ABC, abstractmethod
from typing import Iterator

from exactly_lib.type_val_deps.types.path.path_ddv import DescribedPath
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcher, FileMatcherModel
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace


class FileModel(ABC):
    @property
    @abstractmethod
    def path(self) -> DescribedPath:
        pass

    @property
    @abstractmethod
    def relative_to_root_dir(self) -> pathlib.Path:
        pass

    @abstractmethod
    def as_file_matcher_model(self) -> FileMatcherModel:
        pass


class FilesMatcherModel(ABC):
    @abstractmethod
    def files(self) -> Iterator[FileModel]:
        pass

    @abstractmethod
    def sub_set(self, selector: FileMatcher) -> 'FilesMatcherModel':
        """
        :return a new object that represents a sub set of this object.
        """
        pass

    @abstractmethod
    def prune(self, dir_selector: FileMatcher) -> 'FilesMatcherModel':
        """
        :return a new object that represents a variant of this object with pruned directories.
        """
        pass


FilesMatcher = MatcherWTrace[FilesMatcherModel]
