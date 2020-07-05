import itertools
from typing import Callable

from exactly_lib.type_system.logic import line_matcher
from exactly_lib.type_system.logic.string_transformer import StringTransformerModel
from exactly_lib_test.type_system.logic.string_transformer.test_resources import StringTransformerTestImplBase


class MyNonIdentityTransformer(StringTransformerTestImplBase):
    @property
    def is_identity_transformer(self) -> bool:
        return False

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        return map(lambda s: 'not identity', lines)


class MyToUppercaseTransformer(StringTransformerTestImplBase):
    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        return map(str.upper, lines)


class MyCountNumUppercaseCharactersTransformer(StringTransformerTestImplBase):
    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        return map(get_number_of_uppercase_characters, lines)


def get_number_of_uppercase_characters(line: str) -> str:
    ret_val = 0
    for ch in line:
        if ch.isupper():
            ret_val += 1
    return str(ret_val)


class DuplicateWordsTransformer(StringTransformerTestImplBase):
    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        return map(_with_preserved_new_line_ending(self._do_it), lines)

    @staticmethod
    def _do_it(line: str) -> str:
        words = line.split()
        return ' '.join(itertools.chain.from_iterable(map(lambda x: [x, x], words)))


class DeleteInitialWordTransformer(StringTransformerTestImplBase):
    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        return map(_with_preserved_new_line_ending(self._do_it), lines)

    @staticmethod
    def _do_it(line: str) -> str:
        words = line.split()
        if words:
            del words[0]
        return ' '.join(words)


class KeepSingleLine(StringTransformerTestImplBase):
    def __init__(self, line_num_to_keep: int):
        self.line_num_to_keep = line_num_to_keep

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        line_num_to_keep = self.line_num_to_keep
        for line in enumerate(lines, line_matcher.FIRST_LINE_NUMBER):
            if line[0] == line_num_to_keep:
                yield line[1]
                break


def _with_preserved_new_line_ending(new_line_agnostic_modifier: Callable[[str], str]) -> Callable[[str], str]:
    def ret_val(x: str) -> str:
        has_new_line = len(x) > 0 and x[-1] == '\n'
        if has_new_line:
            return new_line_agnostic_modifier(x[:-1]) + '\n'
        else:
            return new_line_agnostic_modifier(x)

    return ret_val
