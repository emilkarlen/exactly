import os
from abc import ABC, abstractmethod

from exactly_lib.impls.file_properties import FileType
from exactly_lib.type_val_deps.types.path.path_ddv import DescribedPath
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace


class FileTypeAccess(ABC):
    @abstractmethod
    def is_type(self, expected: FileType) -> bool:
        raise NotImplementedError('abstract method')

    @abstractmethod
    def stat(self, follow_sym_links=True) -> os.stat_result:
        raise NotImplementedError('abstract method')


class FileMatcherModel(ABC):
    @property
    @abstractmethod
    def path(self) -> DescribedPath:
        """Path of the file to match. May or may not exist."""
        raise NotImplementedError('abstract method')

    @property
    @abstractmethod
    def file_type_access(self) -> FileTypeAccess:
        raise NotImplementedError('abstract method')


FileMatcher = MatcherWTrace[FileMatcherModel]
