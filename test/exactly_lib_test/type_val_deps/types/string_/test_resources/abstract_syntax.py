from abc import ABC

from exactly_lib_test.symbol.test_resources import token_sequences
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.test_resources.abstract_syntax import DataTypeAbsStx


class StringAbsStx(DataTypeAbsStx, ABC):
    pass


class StringReferenceAbsStx(StringAbsStx):
    def __init__(self, symbol_name: str):
        self._symbol_name = symbol_name

    @property
    def name(self) -> str:
        return self._symbol_name

    def tokenization(self) -> TokenSequence:
        return token_sequences.SymbolReferenceAsReferenceSyntax(self._symbol_name)
