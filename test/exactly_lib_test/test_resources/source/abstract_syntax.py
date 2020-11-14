from abc import ABC, abstractmethod

from exactly_lib_test.test_resources.source.token_sequence import TokenSequence


class AbstractSyntax(ABC):
    """
    Base class for Abstract Syntax elements,
    as a tool for generating source code for testing.
    """

    @abstractmethod
    def tokenization(self) -> TokenSequence:
        pass
