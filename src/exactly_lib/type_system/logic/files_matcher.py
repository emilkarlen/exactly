import pathlib
from abc import ABC, abstractmethod
from typing import Iterator, Optional

from exactly_lib.type_system.data.path_ddv import DescribedPathPrimitive
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.err_msg.prop_descr import PropertyDescriptor
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.type_system.logic.matcher_base_class import MatcherAdv, MatcherWTraceAndNegation, MatcherDdv


class ErrorMessageInfo(ABC):
    @abstractmethod
    def property_descriptor(self, property_name: str) -> PropertyDescriptor:
        pass


class FileModel(ABC):
    @property
    @abstractmethod
    def path(self) -> DescribedPathPrimitive:
        pass

    @property
    @abstractmethod
    def relative_to_root_dir(self) -> pathlib.Path:
        pass


class FilesMatcherModel(ABC):
    @property
    @abstractmethod
    def error_message_info(self) -> ErrorMessageInfo:
        pass

    @abstractmethod
    def files(self) -> Iterator[FileModel]:
        pass

    @abstractmethod
    def sub_set(self, selector: FileMatcher) -> 'FilesMatcherModel':
        """
        :return a new object that represents a sub set of this object.
        """
        pass


class FilesMatcher(MatcherWTraceAndNegation[FilesMatcherModel], ABC):
    @property
    def option_description(self) -> str:
        return 'todo'

    @property
    @abstractmethod
    def negation(self) -> 'FilesMatcher':
        pass

    @abstractmethod
    def matches_emr(self, files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        """
        :raises HardErrorException: In case of HARD ERROR
        :return: None iff match
        """
        pass

    def _new_tb(self) -> TraceBuilder:
        return TraceBuilder(self.name)


FilesMatcherAdv = MatcherAdv[FilesMatcherModel]

FilesMatcherDdv = MatcherDdv[FilesMatcherModel]
