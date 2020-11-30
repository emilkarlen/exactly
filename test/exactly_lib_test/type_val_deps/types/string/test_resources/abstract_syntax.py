from abc import ABC
from typing import Optional, Sequence

from exactly_lib.util.parse.token import QuoteType
from exactly_lib.util.str_ import misc_formatting
from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.test_resources.source import layout
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.string.test_resources import here_doc
from exactly_lib_test.util.test_resources import quoting


class StringAbsStx(AbstractSyntax, ABC):
    pass


class NonHereDocStringAbsStx(StringAbsStx, ABC):
    pass


class StringLiteralAbsStx(NonHereDocStringAbsStx):
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
        if not new_line_ended_value or new_line_ended_value[-1] != '\n':
            raise ValueError('Invalid contents: ' + repr(new_line_ended_value))

    @staticmethod
    def of_lines__wo_new_lines(lines: Sequence[str],
                               marker: str = 'EOF',
                               ) -> 'StringHereDocAbsStx':
        return StringHereDocAbsStx(misc_formatting.lines_content(lines), marker)

    def tokenization(self) -> TokenSequence:
        return TokenSequence.sequence([self._doc_token(), layout.NEW_LINE_IF_NOT_FIRST_OR_LAST])

    def _doc_token(self) -> str:
        return ''.join([
            here_doc.here_doc_start_token(self.marker),
            '\n',
            self.value,
            self.marker,
        ])


class StringSymbolAbsStx(NonHereDocStringAbsStx):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def tokenization(self) -> TokenSequence:
        return symbol_tok_seq.SymbolReferenceAsReferenceSyntax(self.symbol_name)
