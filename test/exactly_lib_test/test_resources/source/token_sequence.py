import itertools
from abc import ABC, abstractmethod
from typing import Union, Sequence, List

from exactly_lib_test.test_resources.source import layout
from exactly_lib_test.test_resources.source.layout import LayoutAble, LayoutSpec

Token = Union[LayoutAble, str]


class TokenSequence(ABC):
    @staticmethod
    def empty() -> 'TokenSequence':
        return _Sequence(())

    @staticmethod
    def singleton(token: Token) -> 'TokenSequence':
        return _Sequence((token,))

    @staticmethod
    def sequence(tokens: Sequence[Token]) -> 'TokenSequence':
        return _Sequence(tokens)

    @staticmethod
    def concat(sequences: Sequence['TokenSequence']) -> 'TokenSequence':
        return _Concat(sequences)

    @staticmethod
    def new_line() -> 'TokenSequence':
        return _Sequence(('\n',))

    @staticmethod
    def optional_new_line() -> 'TokenSequence':
        return _Sequence((layout.OPTIONAL_NEW_LINE,))

    @property
    @abstractmethod
    def tokens(self) -> Sequence[Token]:
        pass

    def layout(self, spec: LayoutSpec) -> str:
        str_fragments = _non_empty_str_fragments_of_tokens(self.tokens, spec)

        if not str_fragments:
            return ''

        fragments_w_separators = [str_fragments[0]]

        next_token_separator = (
            ''
            if str_fragments[0][-1] == '\n'
            else
            spec.token_separator
        )

        for non_empty_fragment in str_fragments[1:]:
            fragments_w_separators += _fragments_for_fragment(next_token_separator, non_empty_fragment)
            if non_empty_fragment[-1] == '\n':
                next_token_separator = ''
            else:
                next_token_separator = spec.token_separator

        return ''.join(fragments_w_separators)


def _fragments_for_fragment(token_separator: str, non_empty_fragment: str) -> List[str]:
    return (
        [non_empty_fragment]
        if non_empty_fragment[0] == '\n'
        else
        [token_separator, non_empty_fragment]
    )


def _non_empty_str_fragments_of_tokens(tokens: Sequence[Token], spec: LayoutSpec) -> List[str]:
    return list(
        filter(
            _is_not_empty_string,
            itertools.chain.from_iterable([
                _str_fragments_of_token(token, spec)
                for token in tokens
            ])
        )
    )


def _str_fragments_of_token(token: Token, spec: LayoutSpec) -> Sequence[str]:
    if isinstance(token, LayoutAble):
        return token.layout(spec)
    else:
        return [token]


def _is_not_empty_string(s: str) -> bool:
    return s != ''


class _Sequence(TokenSequence):
    def __init__(self, tokens: Sequence[Token]):
        self._tokens = tokens

    @property
    def tokens(self) -> Sequence[Token]:
        return self._tokens


class _Concat(TokenSequence):
    def __init__(self, token_sequences: Sequence[TokenSequence]):
        self.token_sequences = token_sequences

    @property
    def tokens(self) -> Sequence[Token]:
        ret_val = []

        for sequence in self.token_sequences:
            ret_val += sequence.tokens

        return ret_val
