from typing import Sequence, Optional, Callable

from exactly_lib_test.test_resources.source import token_sequences
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence


class OptionalAbsStx(AbstractSyntax):
    def __init__(self,
                 optional: Optional[AbstractSyntax],
                 tokenizer: Callable[[TokenSequence], TokenSequence],
                 ):
        self._optional = optional
        self._tokenizer = tokenizer

    def tokenization(self) -> TokenSequence:
        return (
            TokenSequence.empty()
            if self._optional is None
            else
            self._tokenizer(self._optional.tokenization())
        )


class OptionallyOnNewLine(AbstractSyntax):
    def __init__(self, syntax: AbstractSyntax):
        self._syntax = syntax

    def tokenization(self) -> TokenSequence:
        element_tokens = self._syntax.tokenization()
        return (
            TokenSequence.empty()
            if not element_tokens
            else
            TokenSequence.concat([
                TokenSequence.optional_new_line(),
                element_tokens,
            ])
        )


class DelegateAbsStx(AbstractSyntax):
    def __init__(self, delegate: AbstractSyntax):
        self._delegate = delegate

    def tokenization(self) -> TokenSequence:
        return self._delegate.tokenization()


class InfixOperatorAbsStx(AbstractSyntax):
    def __init__(self,
                 operator: str,
                 operands: Sequence[AbstractSyntax],
                 within_parens: bool,
                 allow_elements_on_separate_lines: bool,
                 ):
        self._operator = operator
        self._operands = operands
        self._within_parens = within_parens
        self._allow_elements_on_separate_lines = allow_elements_on_separate_lines

    def tokenization(self) -> TokenSequence:
        operands = [operand.tokenization() for operand in self._operands]
        return token_sequences.maybe_within_parens(
            token_sequences.InfixOperator(self._operator,
                                          operands,
                                          self._allow_elements_on_separate_lines),
            self._within_parens
        )
