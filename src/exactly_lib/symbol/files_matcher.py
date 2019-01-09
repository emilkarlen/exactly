import pathlib
from abc import ABC, abstractmethod
from typing import Optional, Iterator

from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.resolver_structure import LogicValueResolver, FileMatcherResolver
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.error_message import ErrorMessageResolver, PropertyDescriptor
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util.file_utils import TmpDirFileSpace
from exactly_lib.util.symbol_table import SymbolTable


class Environment:
    def __init__(self,
                 path_resolving_environment: PathResolvingEnvironmentPreOrPostSds,
                 tmp_files_space: TmpDirFileSpace,
                 ):
        self.path_resolving_environment = path_resolving_environment
        self.tmp_files_space = tmp_files_space
        self.symbols = path_resolving_environment.symbols


class ErrorMessageInfo(ABC):
    @abstractmethod
    def property_descriptor(self, property_name: str) -> PropertyDescriptor:
        pass


class FileModel(ABC):
    @property
    @abstractmethod
    def path(self) -> pathlib.Path:
        pass

    @property
    @abstractmethod
    def relative_to_root_dir(self) -> pathlib.Path:
        pass

    @property
    @abstractmethod
    def relative_to_root_dir_as_path_value(self) -> FileRef:
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
    def sub_set(self, selector: FileMatcherResolver):
        """
        :return a new object that represents a sub set of this object.

        :rtype FilesMatcherModel
        """
        pass


class FilesMatcherValue(ABC):
    @property
    @abstractmethod
    def negation(self):
        """
        :rtype FilesMatcherValue
        :return: A matcher that matches the negation of this matcher
        """
        pass

    @abstractmethod
    def matches(self,
                environment: Environment,
                files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        """
        :raises HardErrorException: In case of HARD ERROR
        :return: None iff match
        """
        pass


class FilesMatcherResolver(LogicValueResolver, ABC):
    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.FILES_MATCHER

    @property
    def value_type(self) -> ValueType:
        return ValueType.FILES_MATCHER

    @abstractmethod
    def validator(self) -> PreOrPostSdsValidator:
        pass

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> FilesMatcherValue:
        pass
