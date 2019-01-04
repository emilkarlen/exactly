from abc import ABC, abstractmethod
from typing import Optional

from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.type_system.error_message import ErrorMessageResolver


class FilesSource:
    def __init__(self,
                 path_of_dir: FileRefResolver):
        self._path_of_dir = path_of_dir

    @property
    def path_of_dir(self) -> FileRefResolver:
        return self._path_of_dir


class FilesMatcherResolver(ObjectWithTypedSymbolReferences, ABC):
    @abstractmethod
    def validator(self) -> PreOrPostSdsValidator:
        pass

    @abstractmethod
    def matches(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                files_source: FilesSource) -> Optional[ErrorMessageResolver]:
        pass
