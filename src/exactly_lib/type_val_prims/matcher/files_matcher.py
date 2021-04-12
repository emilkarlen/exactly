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
        raise NotImplementedError('abstract method')

    @property
    @abstractmethod
    def relative_to_root_dir(self) -> pathlib.Path:
        raise NotImplementedError('abstract method')

    @abstractmethod
    def as_file_matcher_model(self) -> FileMatcherModel:
        raise NotImplementedError('abstract method')


class FilesMatcherModel(ABC):
    @abstractmethod
    def files(self) -> Iterator[FileModel]:
        raise NotImplementedError('abstract method')

    @abstractmethod
    def sub_set(self, selector: FileMatcher) -> 'FilesMatcherModel':
        """
        :return a new object that represents a sub set of this object.
        """
        raise NotImplementedError('abstract method')

    @abstractmethod
    def prune(self, dir_selector: FileMatcher) -> 'FilesMatcherModel':
        """
        :return a new object that represents a variant of this object with pruned directories.
        """
        raise NotImplementedError('abstract method')


FilesMatcher = MatcherWTrace[FilesMatcherModel]
