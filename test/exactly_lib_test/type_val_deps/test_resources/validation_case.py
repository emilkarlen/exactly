from abc import ABC, abstractmethod

from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.type_val_deps.test_resources.validation.validation import ValidationAssertions


class ValidationCaseWSymbolContextAndAssertion(ABC):
    @property
    @abstractmethod
    def symbol_context(self) -> SymbolContext:
        pass

    @property
    @abstractmethod
    def assertion(self) -> ValidationAssertions:
        pass
