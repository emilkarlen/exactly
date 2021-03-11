from abc import ABC, abstractmethod

from exactly_lib_test.impls.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.type_val_deps.types.files_source.test_resources.symbol_context import FilesSourceSymbolContext


class ValidationCaseWSymbolContextAndAssertion(ABC):
    @property
    @abstractmethod
    def symbol_context(self) -> FilesSourceSymbolContext:
        pass

    @property
    @abstractmethod
    def assertion(self) -> ValidationAssertions:
        pass
