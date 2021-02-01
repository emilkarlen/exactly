from abc import ABC

from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence


class LineMatcherAbsStx(AbstractSyntax, ABC):
    pass


class LineMatcherSymbolReferenceAbsStx(LineMatcherAbsStx):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def tokenization(self) -> TokenSequence:
        return symbol_tok_seq.SymbolReferenceAsEitherPlainNameOrReferenceSyntax(self.symbol_name)
