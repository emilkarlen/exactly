from abc import ABC

from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.test_resources.abstract_syntax import DataTypeAbsStx


class PathAbsStx(DataTypeAbsStx, ABC):
    pass


class PathSymbolReferenceAbsStx(PathAbsStx):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def tokenization(self) -> TokenSequence:
        return symbol_tok_seq.SymbolReferenceAsReferenceSyntax(self.symbol_name)


class CustomPathAbsStx(PathAbsStx):
    """For expressing invalid syntax."""

    def __init__(self, tokens: TokenSequence):
        self._tokens = tokens

    @staticmethod
    def empty() -> PathAbsStx:
        return CustomPathAbsStx(TokenSequence.empty())

    @staticmethod
    def singleton(token: str) -> PathAbsStx:
        return CustomPathAbsStx(TokenSequence.singleton(token))

    @staticmethod
    def of_str(s: str) -> PathAbsStx:
        return CustomPathAbsStx(TokenSequence.singleton(s))

    def tokenization(self) -> TokenSequence:
        return self._tokens
