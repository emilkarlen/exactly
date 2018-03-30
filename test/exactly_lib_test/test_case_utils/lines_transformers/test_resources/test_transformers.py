from typing import Iterable

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer


class MyNonIdentityTransformer(LinesTransformer):
    @property
    def is_identity_transformer(self) -> bool:
        return False

    def transform(self, tcds: HomeAndSds, lines: Iterable[str]) -> Iterable[str]:
        return map(lambda s: 'not identity', lines)


class MyToUppercaseTransformer(LinesTransformer):
    def transform(self, tcds: HomeAndSds, lines: Iterable[str]) -> Iterable[str]:
        return map(str.upper, lines)


class MyCountNumUppercaseCharactersTransformer(LinesTransformer):
    def transform(self, tcds: HomeAndSds, lines: Iterable[str]) -> Iterable[str]:
        return map(get_number_of_uppercase_characters, lines)


def get_number_of_uppercase_characters(line: str) -> str:
    ret_val = 0
    for ch in line:
        if ch.isupper():
            ret_val += 1
    return str(ret_val)
