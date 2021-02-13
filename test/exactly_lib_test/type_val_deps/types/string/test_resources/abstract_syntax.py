from abc import ABC

from exactly_lib_test.symbol.test_resources import token_sequences
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence


class StringAbsStx(AbstractSyntax, ABC):
    pass


class NonHereDocStringAbsStx(StringAbsStx, ABC):
    pass


class StringReferenceAbsStx(NonHereDocStringAbsStx):
    def __init__(self, symbol_name: str):
        self._symbol_name = symbol_name

    def tokenization(self) -> TokenSequence:
        return token_sequences.SymbolReferenceAsReferenceSyntax(self._symbol_name)
