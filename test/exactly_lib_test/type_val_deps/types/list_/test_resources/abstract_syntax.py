from abc import ABC
from typing import Sequence, Optional

from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.string.test_resources import abstract_syntaxes as str_abs_stx
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntax import NonHereDocStringAbsStx


class ListElementAbsStx(AbstractSyntax, ABC):
    pass


class ListElementSymbolReferenceAbsStx(ListElementAbsStx):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def tokenization(self) -> TokenSequence:
        return symbol_tok_seq.SymbolReferenceAsReferenceSyntax(self.symbol_name)


class ListElementStringAbsStx(ListElementAbsStx):
    def __init__(self, string: NonHereDocStringAbsStx):
        self.string = string

    def tokenization(self) -> TokenSequence:
        return self.string.tokenization()


class ListAbsStx(AbstractSyntax):
    def __init__(self, elements: Sequence[ListElementAbsStx]):
        self.elements = elements

    @staticmethod
    def empty() -> 'ListAbsStx':
        return ListAbsStx(())

    @staticmethod
    def symbol_reference(symbol_name: str) -> 'ListSymbolReferenceAbsStx':
        return ListSymbolReferenceAbsStx(symbol_name)

    @staticmethod
    def singleton(element: ListElementAbsStx) -> 'ListAbsStx':
        return ListAbsStx((element,))

    @staticmethod
    def singleton_string(element: NonHereDocStringAbsStx) -> 'ListAbsStx':
        return ListAbsStx.singleton(ListElementStringAbsStx(element))

    @staticmethod
    def singleton_string__str(element: str,
                              quoting: Optional[QuoteType] = None,
                              ) -> 'ListAbsStx':
        return ListAbsStx.singleton_string(str_abs_stx.StringLiteralAbsStx(element, quoting))

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            element.tokenization()
            for element in self.elements
        ])


class ListSymbolReferenceAbsStx(ListAbsStx):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name
        super().__init__((ListElementSymbolReferenceAbsStx(symbol_name),))
