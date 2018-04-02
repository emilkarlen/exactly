import itertools
from typing import Iterable, Callable

from exactly_lib.test_case_utils.lines_transformer.transformers import CustomLinesTransformer
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer


class MyNonIdentityTransformer(LinesTransformer):
    @property
    def is_identity_transformer(self) -> bool:
        return False

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(lambda s: 'not identity', lines)


class MyToUppercaseTransformer(CustomLinesTransformer):
    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(str.upper, lines)


class MyCountNumUppercaseCharactersTransformer(LinesTransformer):
    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(get_number_of_uppercase_characters, lines)


def get_number_of_uppercase_characters(line: str) -> str:
    ret_val = 0
    for ch in line:
        if ch.isupper():
            ret_val += 1
    return str(ret_val)


class DuplicateWordsTransformer(CustomLinesTransformer):
    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(_with_preserved_new_line_ending(self._do_it), lines)

    @staticmethod
    def _do_it(line: str) -> str:
        words = line.split()
        return ' '.join(itertools.chain.from_iterable(map(lambda x: [x, x], words)))


class DeleteInitialWordTransformer(CustomLinesTransformer):
    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(_with_preserved_new_line_ending(self._do_it), lines)

    @staticmethod
    def _do_it(line: str) -> str:
        words = line.split()
        if words:
            del words[0]
        return ' '.join(words)


class DeleteEverythingTransformer(CustomLinesTransformer):
    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return []


def _with_preserved_new_line_ending(new_line_agnostic_modifier: Callable[[str], str]) -> Callable[[str], str]:
    def ret_val(x: str) -> str:
        has_new_line = len(x) > 0 and x[-1] == '\n'
        if has_new_line:
            return new_line_agnostic_modifier(x[:-1]) + '\n'
        else:
            return new_line_agnostic_modifier(x)

    return ret_val
