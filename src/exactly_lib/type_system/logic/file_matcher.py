from abc import ABC, abstractmethod

from exactly_lib.type_system.data.path_ddv import DescribedPathPrimitive
from exactly_lib.type_system.err_msg.prop_descr import FilePropertyDescriptorConstructor
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatcherDdv, MatcherAdv


class FileMatcherModel(ABC):
    @property
    @abstractmethod
    def path(self) -> DescribedPathPrimitive:
        """Path of the file to match. May or may not exist."""
        pass

    @property
    @abstractmethod
    def file_descriptor(self) -> FilePropertyDescriptorConstructor:
        pass


FileMatcher = MatcherWTraceAndNegation[FileMatcherModel]

FileMatcherAdv = MatcherAdv[FileMatcherModel]

FileMatcherDdv = MatcherDdv[FileMatcherModel]
