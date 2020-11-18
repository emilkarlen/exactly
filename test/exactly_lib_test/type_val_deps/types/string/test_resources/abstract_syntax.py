from abc import ABC
from typing import Optional

from exactly_lib.definitions.primitives import string
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.util.test_resources import quoting


class StringAbsStx(AbstractSyntax, ABC):
    pass


class StringConstantAbsStx(StringAbsStx):
    def __init__(self,
                 value: str,
                 quoting_: Optional[QuoteType] = None,
                 ):
        self.value = value
        self.quoting = quoting_

    def tokenization(self) -> TokenSequence:
        return TokenSequence.singleton(self._token())

    def _token(self) -> str:
        if self.quoting is None:
            return self.value
        elif self.quoting is QuoteType.SOFT:
            return quoting.surrounded_by_soft_quotes_str(self.value)
        elif self.quoting is QuoteType.HARD:
            return quoting.surrounded_by_hard_quotes_str(self.value)
        else:
            raise ValueError('Invalid quoting: ' + str(self.quoting))


class StringHereDocAbsStx(StringAbsStx):
    def __init__(self,
                 new_line_ended_value: str,
                 marker: str = 'EOF',
                 ):
        self.value = new_line_ended_value
        self.marker = marker

    def tokenization(self) -> TokenSequence:
        return TokenSequence.singleton(self._token())

    def _token(self) -> str:
        return ''.join([
            string.HERE_DOCUMENT_MARKER_PREFIX,
            self.marker,
            '\n',
            self.value,
            self.marker,
            '\n',
        ])


class StringSymbolAbsStx(StringAbsStx):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def tokenization(self) -> TokenSequence:
        return symbol_tok_seq.SymbolReferenceAsReferenceSyntax(self.symbol_name)
