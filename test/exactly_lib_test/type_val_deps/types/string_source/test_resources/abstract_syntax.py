from abc import ABC

from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.test_resources.abstract_syntax import LogicTypeAbsStx


class StringSourceAbsStx(LogicTypeAbsStx, ABC):
    pass


class TransformableStringSourceAbsStx(StringSourceAbsStx, ABC):
    pass


class StringSourceSymbolReferenceAbsStx(TransformableStringSourceAbsStx):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def tokenization(self) -> TokenSequence:
        return symbol_tok_seq.SymbolReferenceAsReferenceSyntax(self.symbol_name)
