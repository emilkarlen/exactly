from typing import Sequence

from exactly_lib_test.test_resources.source import token_sequences
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence


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
