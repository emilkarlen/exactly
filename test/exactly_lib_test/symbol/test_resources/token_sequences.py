from typing import Sequence

from exactly_lib.symbol import symbol_syntax
from exactly_lib_test.test_resources.source.layout import LayoutAble, LayoutSpec
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence, Token


class SymbolReferenceAsReferenceSyntax(TokenSequence):
    def __init__(self, symbol_name: str):
        self._symbol_name = symbol_name

    @property
    def tokens(self) -> Sequence[Token]:
        return (_SymbolReferenceAsReferenceSyntax(self._symbol_name),)


class SymbolReferenceAsEitherPlainNameOrReferenceSyntax(TokenSequence):
    def __init__(self, symbol_name: str):
        self._symbol_name = symbol_name

    @property
    def tokens(self) -> Sequence[Token]:
        return (_SymbolReferenceAsEitherPlainNameOrReferenceSyntax(self._symbol_name),)


class _SymbolReferenceAsReferenceSyntax(LayoutAble):
    def __init__(self, symbol_name: str):
        self._symbol_name = symbol_name

    def layout(self, spec: LayoutSpec) -> Sequence[str]:
        return (symbol_syntax.symbol_reference_syntax_for_name(self._symbol_name),)


class _SymbolReferenceAsEitherPlainNameOrReferenceSyntax(LayoutAble):
    def __init__(self, symbol_name: str):
        self._symbol_name = symbol_name

    def layout(self, spec: LayoutSpec) -> Sequence[str]:
        return (
            (self._symbol_name,)
            if spec.symbol_reference_as_plain_symbol_name
            else
            (symbol_syntax.symbol_reference_syntax_for_name(self._symbol_name),)
        )
