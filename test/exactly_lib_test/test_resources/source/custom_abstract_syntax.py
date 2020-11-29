from typing import Sequence

from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence, Token


class CustomAbstractSyntax(AbstractSyntax):
    def __init__(self, tokens: TokenSequence):
        self._tokens = tokens

    @staticmethod
    def empty() -> AbstractSyntax:
        return CustomAbstractSyntax(TokenSequence.empty())

    @staticmethod
    def singleton(token: Token) -> AbstractSyntax:
        return CustomAbstractSyntax(TokenSequence.singleton(token))

    @staticmethod
    def sequence(tokens: Sequence[Token]) -> AbstractSyntax:
        return CustomAbstractSyntax(TokenSequence.sequence(tokens))

    def tokenization(self) -> TokenSequence:
        return self._tokens


class SequenceAbstractSyntax(AbstractSyntax):
    def __init__(self, elements: Sequence[AbstractSyntax]):
        self._elements = elements

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            element.tokenization()
            for element in self._elements
        ])
