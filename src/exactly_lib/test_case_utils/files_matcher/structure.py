from abc import ABC, abstractmethod
from typing import Optional

from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.type_system.error_message import ErrorMessageResolver
from exactly_lib.util.file_utils import TmpDirFileSpace


class FilesSource:
    def __init__(self,
                 path_of_dir: FileRefResolver):
        self._path_of_dir = path_of_dir

    @property
    def path_of_dir(self) -> FileRefResolver:
        return self._path_of_dir


class HardErrorException(Exception):
    def __init__(self, error: ErrorMessageResolver):
        self._error = error

    @property
    def error(self) -> ErrorMessageResolver:
        return self._error


class Environment:
    def __init__(self,
                 path_resolving_environment: PathResolvingEnvironmentPreOrPostSds,
                 tmp_files_space: TmpDirFileSpace,
                 ):
        self.path_resolving_environment = path_resolving_environment
        self.tmp_files_space = tmp_files_space


class FilesMatcherResolver(ObjectWithTypedSymbolReferences, ABC):
    @abstractmethod
    def validator(self) -> PreOrPostSdsValidator:
        pass

    @abstractmethod
    def matches(self,
                environment: Environment,
                files_source: FilesSource) -> Optional[ErrorMessageResolver]:
        """
        :raises HardErrorException: In case of HARD ERROR
        :return: None iff match
        """
        pass
