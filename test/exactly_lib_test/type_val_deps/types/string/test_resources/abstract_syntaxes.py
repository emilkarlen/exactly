import itertools
import shlex
from typing import Optional, Sequence, AbstractSet

from exactly_lib.util.parse.token import QuoteType
from exactly_lib.util.str_ import misc_formatting
from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.test_resources.source import layout, token_sequence
from exactly_lib_test.test_resources.source.layout import LayoutAble, LayoutSpec, TokenPosition
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence, Token
from exactly_lib_test.type_val_deps.types.string.test_resources import here_doc
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntax import StringAbsStx, \
    NonHereDocStringAbsStx
from exactly_lib_test.util.test_resources import quoting


class StringLiteralAbsStx(NonHereDocStringAbsStx):
    def __init__(self,
                 value: str,
                 quoting_: Optional[QuoteType] = None,
                 ):
        self.value = value
        self.quoting = quoting_

    @staticmethod
    def empty_string() -> 'StringLiteralAbsStx':
        return StringLiteralAbsStx('', QuoteType.HARD)

    @staticmethod
    def of_shlex_quoted(unquoted: str) -> 'StringLiteralAbsStx':
        return StringLiteralAbsStx(shlex.quote(unquoted))

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


QUOTED_STR__SOFT = quoting.surrounded_by_soft_quotes_str('quoted_value__soft')
QUOTED_STR__HARD = quoting.surrounded_by_hard_quotes_str('quoted_value__hard')

MISSING_END_QUOTE_STR__SOFT = quoting.SOFT_QUOTE_CHAR + 'missing_end_quote'
MISSING_END_QUOTE_STR__HARD = quoting.HARD_QUOTE_CHAR + 'missing_end_quote'

MISSING_END_QUOTE__SOFT = StringLiteralAbsStx(MISSING_END_QUOTE_STR__SOFT)
MISSING_END_QUOTE__HARD = StringLiteralAbsStx(MISSING_END_QUOTE_STR__HARD)


class StringConcatAbsStx(NonHereDocStringAbsStx):
    def __init__(self, fragments: Sequence[NonHereDocStringAbsStx]):
        if not fragments:
            raise ValueError('Concatenation must contain at least 1 fragment:' + str(len(fragments)))
        self.fragments = fragments

    def tokenization(self) -> TokenSequence:
        return _StringConcatTokenSequence([
            fragment.tokenization()
            for fragment in self.fragments
        ])


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


class _StringConcatTokenSequence(TokenSequence):
    def __init__(self, fragments: Sequence[TokenSequence]):
        self.fragments = fragments

    @property
    def tokens(self) -> Sequence[Token]:
        return [
            _StringConcatLayoutAble([
                fragment.tokens
                for fragment in self.fragments
            ])]


class _StringConcatLayoutAble(LayoutAble):
    def __init__(self, fragments: Sequence[Sequence[Token]]):
        self.fragments = tuple(itertools.chain.from_iterable(fragments))

    def layout(self,
               spec: LayoutSpec,
               position: AbstractSet[TokenPosition],
               ) -> Sequence[str]:
        str_seq_seq = [
            token_sequence.str_fragments_of_token(token, spec, position)
            for token in self.fragments
        ]
        str_ = ''.join(itertools.chain.from_iterable(str_seq_seq))

        return (str_,)
