from typing import Iterable

from exactly_lib.type_system.logic.lines_transformer import CustomStringTransformer


class ToUpperCaseLinesTransformer(CustomStringTransformer):
    @property
    def is_identity_transformer(self) -> bool:
        return False

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(str.upper, lines)


class ToLowerCaseLinesTransformer(CustomStringTransformer):
    @property
    def is_identity_transformer(self) -> bool:
        return False

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(str.lower, lines)
